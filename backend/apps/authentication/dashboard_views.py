from django.utils import timezone
from django.db.models import Count, Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from datetime import timedelta, date
from apps.employees.models import Employee, Department
from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest
from apps.payroll.models import Payslip, PayrollRun

User = get_user_model()

class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Total employees (approved users)
        total_employees = User.objects.filter(
            approval_status='APPROVED', 
            is_active=True
        ).count()

        # Present today
        today = timezone.now().date()
        present_today = AttendanceRecord.objects.filter(
            date=today,
            status='PRESENT'
        ).count()

        # Pending leave requests
        pending_leaves = LeaveRequest.objects.filter(
            status='PENDING'
        ).count()

        # Pending user approvals
        pending_approvals = User.objects.filter(
            approval_status='PENDING'
        ).count()

        # This month's payroll total
        current_month = today.month
        current_year = today.year
        payroll_this_month = Payslip.objects.filter(
            payroll_run__month=current_month,
            payroll_run__year=current_year
        ).aggregate(total=Sum('net_salary'))['total'] or 0

        return Response({
            "total_employees": total_employees,
            "present_today": present_today,
            "pending_leaves": pending_leaves,
            "pending_approvals": pending_approvals,
            "payroll_this_month": float(payroll_this_month)
        })

class AttendanceTrendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Last 30 days attendance data
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            present_count = AttendanceRecord.objects.filter(
                date=current_date,
                status='PRESENT'
            ).count()
            
            absent_count = AttendanceRecord.objects.filter(
                date=current_date,
                status='ABSENT'
            ).count()
            
            on_leave_count = AttendanceRecord.objects.filter(
                date=current_date,
                status='ON_LEAVE'
            ).count()
            
            trend_data.append({
                "date": current_date.strftime("%m-%d"),
                "present": present_count,
                "absent": absent_count,
                "on_leave": on_leave_count
            })
            
            current_date += timedelta(days=1)
        
        return Response(trend_data)

class DepartmentDistributionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get employee count by department
        departments = Department.objects.annotate(
            employee_count=Count('employee')
        ).values('name', 'employee_count')
        
        data = [
            {
                "department": dept['name'],
                "count": dept['employee_count']
            }
            for dept in departments
        ]
        
        # If no departments, provide sample data
        if not data:
            data = [
                {"department": "Engineering", "count": 0},
                {"department": "HR", "count": 0},
                {"department": "Finance", "count": 0},
                {"department": "Marketing", "count": 0}
            ]
        
        return Response(data)

class RecentActivitiesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = []
        now = timezone.now()
        
        # Recent user approvals
        recent_approvals = User.objects.filter(
            approval_status='APPROVED',
            date_joined__gte=now - timedelta(days=7)
        ).order_by('-date_joined')[:5]
        
        for user in recent_approvals:
            activities.append({
                "actor": "HR Admin",
                "action": f"approved user registration for {user.first_name} {user.last_name}",
                "target": user.email,
                "timestamp": user.date_joined.isoformat()
            })
        
        # Recent leave requests
        recent_leaves = LeaveRequest.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        for leave in recent_leaves:
            activities.append({
                "actor": f"{leave.employee.user.first_name} {leave.employee.user.last_name}",
                "action": f"submitted {leave.leave_type.name.lower()} request",
                "target": f"{leave.start_date} to {leave.end_date}",
                "timestamp": leave.created_at.isoformat()
            })
        
        # Recent attendance records
        recent_attendance = AttendanceRecord.objects.filter(
            date__gte=now.date() - timedelta(days=3),
            status='ABSENT'
        ).order_by('-date')[:3]
        
        for record in recent_attendance:
            activities.append({
                "actor": f"{record.employee.user.first_name} {record.employee.user.last_name}",
                "action": "marked absent",
                "target": record.date.strftime("%Y-%m-%d"),
                "timestamp": now.isoformat()  # Use current time as placeholder
            })
        
        # Sort by timestamp and limit to 10 most recent
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if not activities:
            activities = [{
                "actor": "System",
                "action": "Welcome to HR Dashboard - No recent activities",
                "target": "",
                "timestamp": now.isoformat()
            }]
        
        return Response(activities[:10])