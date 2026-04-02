from io import BytesIO
import csv
import pandas as pd
from django.utils import timezone
from apps.employees.models import Employee
from apps.attendance.models import AttendanceRecord


def build_employee_rows(queryset):
    rows = []
    for emp in queryset:
        rows.append({
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
    return rows


def build_attendance_rows(queryset):
    rows = []
    for record in queryset:
        work_hours = None
        overtime = 0
        if record.check_in and record.check_out:
            duration = record.check_out - record.check_in
            work_hours = duration.total_seconds() / 3600
            if work_hours > 9:
                overtime = work_hours - 9

        rows.append({
            'Date': record.date,
            'Employee': f"{record.employee.user.first_name} {record.employee.user.last_name}",
            'Department': record.employee.department.name if record.employee.department else '',
            'Status': record.status,
            'Check In': record.check_in,
            'Check Out': record.check_out,
            'Work Hours': f"{work_hours:.2f}" if work_hours else '',
            'Overtime': f"{overtime:.2f}" if overtime > 0 else ''
        })
    return rows


def rows_to_csv(rows):
    buffer = BytesIO()
    if not rows:
        buffer.write(b'')
        buffer.seek(0)
        return buffer

    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    buffer.seek(0)
    return buffer


def rows_to_excel(rows):
    buffer = BytesIO()
    df = pd.DataFrame(rows)
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer


def get_employee_queryset(user, permissions):
    if 'view_all_employees' in permissions:
        return Employee.objects.select_related('user', 'department').all()
    if 'view_team_employees' in permissions:
        try:
            manager = Employee.objects.get(user=user)
            return Employee.objects.filter(department=manager.department).select_related('user', 'department')
        except Employee.DoesNotExist:
            return Employee.objects.none()
    return Employee.objects.filter(user=user).select_related('user', 'department')


def get_attendance_queryset(user, permissions, start_date=None, end_date=None):
    queryset = AttendanceRecord.objects.select_related('employee__user')
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    if 'view_team_attendance' in permissions and 'view_attendance_data' not in permissions:
        try:
            manager = Employee.objects.get(user=user)
            team_users = Employee.objects.filter(department=manager.department).values_list('user', flat=True)
            queryset = queryset.filter(employee__user__in=team_users)
        except Employee.DoesNotExist:
            return AttendanceRecord.objects.none()

    return queryset


def generate_report_bytes(report_type, file_format, user, permissions, start_date=None, end_date=None):
    if report_type == 'employees':
        rows = build_employee_rows(get_employee_queryset(user, permissions))
    elif report_type == 'attendance':
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
        rows = build_attendance_rows(get_attendance_queryset(user, permissions, start_date, end_date))
    else:
        rows = []

    if file_format == 'excel':
        return rows_to_excel(rows)

    return rows_to_csv(rows)
