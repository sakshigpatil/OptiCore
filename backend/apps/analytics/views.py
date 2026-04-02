from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from apps.analytics.models import ScheduledReport
from apps.analytics.serializers import ScheduledReportSerializer
from apps.analytics.reporting import generate_report_bytes
from apps.notifications.models import Notification
from apps.employees.models import Employee, Department
from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest
from apps.payroll.models import Payslip
from apps.projects.models import Project, Task
import csv
import json
from datetime import datetime, timedelta
from core.permissions import HasRolePermission
import pandas as pd
from io import BytesIO

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasRolePermission])
def get_dashboard_analytics(request):
    """Get analytics data for dashboard charts"""
    user = request.user
    permissions = getattr(user, 'permissions', get_user_permissions(user))

    cache_key = f"analytics:dashboard:{user.id}:{user.role}"
    cached_payload = cache.get(cache_key)
    if cached_payload:
        return Response(cached_payload)

    analytics_data = {
        'employee_stats': get_employee_stats(user, permissions),
        'attendance_trends': get_attendance_trends(user, permissions),
        'leave_analytics': get_leave_analytics(user, permissions),
        'payroll_summary': get_payroll_summary(user, permissions),
        'department_distribution': get_department_distribution(user, permissions),
    }

    cache.set(cache_key, analytics_data, timeout=60)
    return Response(analytics_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasRolePermission])
def generate_custom_report(request):
    """Generate a custom report based on request parameters."""
    user = request.user
    permissions = getattr(user, 'permissions', get_user_permissions(user))

    report_type = request.data.get('report_type')
    file_format = request.data.get('file_format', 'csv')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    if report_type not in ['employees', 'attendance']:
        return Response({'error': 'Unsupported report type'}, status=status.HTTP_400_BAD_REQUEST)

    if file_format not in ['csv', 'excel']:
        return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

    parsed_start = None
    parsed_end = None

    try:
        if start_date:
            parsed_start = datetime.fromisoformat(start_date).date()
        if end_date:
            parsed_end = datetime.fromisoformat(end_date).date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    buffer = generate_report_bytes(report_type, file_format, user, permissions, parsed_start, parsed_end)

    extension = 'xlsx' if file_format == 'excel' else 'csv'
    filename = f"custom_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    if file_format == 'csv':
        content_type = 'text/csv'

    response = HttpResponse(buffer.getvalue(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


class ScheduledReportViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', '') == 'ADMIN_HR':
            return ScheduledReport.objects.all()
        return ScheduledReport.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        report = self.get_object()
        permissions = getattr(report.owner, 'permissions', get_user_permissions(report.owner))

        buffer = generate_report_bytes(report.report_type, report.file_format, report.owner, permissions)
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        ext = 'xlsx' if report.file_format == 'excel' else 'csv'
        filename = f"{report.report_type}_{report.owner_id}_{timestamp}.{ext}"

        report.last_report_file.save(filename, ContentFile(buffer.getvalue()), save=False)
        report.last_run_at = timezone.now()
        report.last_status = 'success'
        report.last_message = 'Report generated successfully'
        report.next_run_at = report.compute_next_run(timezone.now())
        report.save()

        report_url = None
        if report.last_report_file:
            report_url = request.build_absolute_uri(report.last_report_file.url)

        Notification.objects.create(
            recipient=report.owner,
            title=f"Scheduled report ready: {report.name}",
            message=f"Your {report.report_type} report is ready.",
            notification_type='INFO',
            action_url=report_url
        )

        return Response({
            'message': 'Report generated',
            'file': report_url
        }, status=status.HTTP_200_OK)

def get_employee_stats(user, permissions):
    """Get employee statistics for dashboard"""
    base_queryset = Employee.objects.all()

    if 'view_team_employees' in permissions and 'view_all_employees' not in permissions:
        try:
            manager = Employee.objects.get(user=user)
            base_queryset = base_queryset.filter(department=manager.department)
        except Employee.DoesNotExist:
            base_queryset = Employee.objects.none()

    return {
        'total_employees': base_queryset.count(),
        'active_employees': base_queryset.filter(user__is_active=True).count(),
        'new_hires_this_month': base_queryset.filter(
            hire_date__year=datetime.now().year,
            hire_date__month=datetime.now().month
        ).count(),
        'departments_count': base_queryset.values('department').distinct().count()
    }

def get_attendance_trends(user, permissions):
    """Get attendance trends for the last 30 days"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    base_queryset = AttendanceRecord.objects.filter(date__range=[start_date, end_date])

    if 'view_team_attendance' in permissions and 'view_attendance_data' not in permissions:
        try:
            manager = Employee.objects.get(user=user)
            team_users = Employee.objects.filter(department=manager.department).values_list('user', flat=True)
            base_queryset = base_queryset.filter(employee__user__in=team_users)
        except Employee.DoesNotExist:
            base_queryset = AttendanceRecord.objects.none()

    # Group by date and status
    trends = []
    current_date = start_date
    while current_date <= end_date:
        day_records = base_queryset.filter(date=current_date)
        trends.append({
            'date': current_date.isoformat(),
            'present': day_records.filter(status='PRESENT').count(),
            'absent': day_records.filter(status='ABSENT').count(),
            'late': day_records.filter(status='LATE').count(),
            'half_day': day_records.filter(status='HALF_DAY').count()
        })
        current_date += timedelta(days=1)

    return trends

def get_leave_analytics(user, permissions):
    """Get leave analytics data"""
    base_queryset = LeaveRequest.objects.all()

    if 'view_team_leaves' in permissions and 'view_leave_data' not in permissions:
        try:
            manager = Employee.objects.get(user=user)
            team_users = Employee.objects.filter(department=manager.department).values_list('user', flat=True)
            base_queryset = base_queryset.filter(employee__user__in=team_users)
        except Employee.DoesNotExist:
            base_queryset = LeaveRequest.objects.none()

    return {
        'total_requests': base_queryset.count(),
        'pending': base_queryset.filter(status='PENDING').count(),
        'approved': base_queryset.filter(status='APPROVED').count(),
        'rejected': base_queryset.filter(status='REJECTED').count(),
        'this_month': base_queryset.filter(
            created_at__year=datetime.now().year,
            created_at__month=datetime.now().month
        ).count()
    }

def get_payroll_summary(user, permissions):
    """Get payroll summary data"""
    base_queryset = Payslip.objects.all()

    if 'view_basic_payroll' in permissions and 'view_payroll_data' not in permissions:
        base_queryset = base_queryset.filter(employee=user)

    current_month = datetime.now().month
    current_year = datetime.now().year

    return {
        'total_payslips': base_queryset.count(),
        'total_amount': base_queryset.aggregate(total=Sum('net_salary'))['total'] or 0,
        'average_salary': base_queryset.aggregate(avg=Avg('net_salary'))['avg'] or 0,
        'this_month_payslips': base_queryset.filter(
            payroll_run__year=current_year,
            payroll_run__month=current_month
        ).count()
    }

def get_department_distribution(user, permissions):
    """Get department distribution data"""
    base_queryset = Employee.objects.all()

    if 'view_team_employees' in permissions and 'view_all_employees' not in permissions:
        try:
            manager = Employee.objects.get(user=user)
            base_queryset = base_queryset.filter(department=manager.department)
        except Employee.DoesNotExist:
            base_queryset = Employee.objects.none()

    distribution = base_queryset.values('department__name').annotate(
        count=Count('id')
    ).order_by('-count')

    return list(distribution)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasRolePermission])
def export_employee_data(request):
    """Export employee data to CSV/Excel"""
    user = request.user
    format_type = request.GET.get('file_format') or request.GET.get('format', 'csv')

    # Get user permissions
    permissions = getattr(user, 'permissions', get_user_permissions(user))

    # Base queryset with permission filtering
    if 'view_all_employees' in permissions:
        employees = Employee.objects.select_related('user', 'department').all()
    elif 'view_team_employees' in permissions:
        # Managers see only their team
        try:
            manager = Employee.objects.get(user=user)
            employees = Employee.objects.filter(
                department=manager.department
            ).select_related('user', 'department')
        except Employee.DoesNotExist:
            employees = Employee.objects.none()
    else:
        # Employees see only themselves
        employees = Employee.objects.filter(user=user).select_related('user', 'department')

    if format_type == 'csv':
        return export_employee_csv(employees)
    elif format_type == 'excel':
        return export_employee_excel(employees)
    else:
        return Response({'error': 'Unsupported format'}, status=400)

def export_employee_csv(employees):
    """Export employees to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'Name', 'Email', 'Department', 'Position',
        'Salary', 'Hire Date', 'Manager', 'Status'
    ])

    for emp in employees:
        writer.writerow([
            emp.id,
            f"{emp.user.first_name} {emp.user.last_name}",
            emp.user.email,
            emp.department.name if emp.department else '',
            emp.position or '',
            emp.salary or '',
            emp.hire_date,
            emp.manager.user.get_full_name() if emp.manager else '',
            'Active' if emp.user.is_active else 'Inactive'
        ])

    return response

def export_employee_excel(employees):
    """Export employees to Excel"""
    data = []
    for emp in employees:
        data.append({
            'Employee ID': emp.id,
            'Name': f"{emp.user.first_name} {emp.user.last_name}",
            'Email': emp.user.email,
            'Department': emp.department.name if emp.department else '',
            'Position': emp.position or '',
            'Salary': emp.salary or '',
            'Hire Date': emp.hire_date,
            'Manager': emp.manager.user.get_full_name() if emp.manager else '',
            'Status': 'Active' if emp.user.is_active else 'Inactive'
        })

    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasRolePermission])
def export_attendance_data(request):
    """Export attendance data with analytics"""
    user = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    format_type = request.GET.get('file_format') or request.GET.get('format', 'csv')

    permissions = getattr(user, 'permissions', get_user_permissions(user))

    # Date filtering
    queryset = AttendanceRecord.objects.select_related('employee__user')
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    # Permission filtering
    if 'view_team_attendance' in permissions and 'view_attendance_data' not in permissions:
        try:
            manager = Employee.objects.get(user=user)
            team_users = Employee.objects.filter(
                department=manager.department
            ).values_list('user', flat=True)
            queryset = queryset.filter(employee__user__in=team_users)
        except Employee.DoesNotExist:
            queryset = AttendanceRecord.objects.none()

    if format_type == 'csv':
        return export_attendance_csv(queryset)
    elif format_type == 'excel':
        return export_attendance_excel(queryset)
    else:
        return Response({'error': 'Unsupported format'}, status=400)

def export_attendance_csv(queryset):
    """Export attendance to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Employee', 'Department', 'Status', 'Check In', 'Check Out',
        'Work Hours', 'Overtime'
    ])

    for record in queryset:
        work_hours = None
        overtime = 0
        if record.check_in and record.check_out:
            duration = record.check_out - record.check_in
            work_hours = duration.total_seconds() / 3600
            if work_hours > 9:  # Assuming 9 hours is standard
                overtime = work_hours - 9

        writer.writerow([
            record.date,
            f"{record.employee.user.first_name} {record.employee.user.last_name}",
            record.employee.department.name if record.employee.department else '',
            record.status,
            record.check_in,
            record.check_out,
            f"{work_hours:.2f}" if work_hours else '',
            f"{overtime:.2f}" if overtime > 0 else ''
        ])

    return response

def export_attendance_excel(queryset):
    """Export attendance to Excel with analytics"""
    data = []
    for record in queryset:
        work_hours = None
        overtime = 0
        if record.check_in and record.check_out:
            duration = record.check_out - record.check_in
            work_hours = duration.total_seconds() / 3600
            if work_hours > 9:
                overtime = work_hours - 9

        data.append({
            'Date': record.date,
            'Employee': f"{record.employee.user.first_name} {record.employee.user.last_name}",
            'Department': record.employee.department.name if record.employee.department else '',
            'Status': record.status,
            'Check In': record.check_in,
            'Check Out': record.check_out,
            'Work Hours': f"{work_hours:.2f}" if work_hours else '',
            'Overtime': f"{overtime:.2f}" if overtime > 0 else ''
        })

    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="attendance.xlsx"'
    return response

def get_user_permissions(user):
    """Get user permissions based on role"""
    permissions = []

    if hasattr(user, 'role'):
        if user.role == 'ADMIN_HR':
            permissions.extend([
                'view_all_employees', 'view_all_departments', 'view_attendance_data',
                'view_leave_data', 'view_payroll_data', 'view_project_data',
                'view_analytics', 'export_data'
            ])
        elif user.role == 'MANAGER':
            permissions.extend([
                'view_team_employees', 'view_department_stats', 'view_team_attendance',
                'view_team_leaves', 'view_basic_payroll', 'view_team_projects',
                'view_team_performance', 'export_team_data'
            ])
        elif user.role == 'EMPLOYEE':
            permissions.extend([
                'view_own_profile', 'view_own_attendance', 'view_own_leaves',
                'view_basic_payroll', 'export_own_data'
            ])

    return permissions