#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from apps.employees.models import Employee, Department
from django.contrib.auth import get_user_model

User = get_user_model()

print('=== CURRENT HRMS EMPLOYEE DATABASE ===\n')

print('📊 SUMMARY:')
print(f'  Total Users: {User.objects.count()}')
print(f'  Total Employee Profiles: {Employee.objects.count()}')
print(f'  Total Departments: {Department.objects.count()}\n')

print('👥 USER ROLES:')
for role in ['ADMIN_HR', 'MANAGER', 'EMPLOYEE']:
    count = User.objects.filter(role=role).count()
    print(f'  {role}: {count} users')

print('\n🏢 DEPARTMENTS:')
for dept in Department.objects.all():
    emp_count = Employee.objects.filter(department=dept).count()
    print(f'  {dept.name}: {emp_count} employees')

print('\n👨‍💼 EMPLOYEE PROFILES:')
for emp in Employee.objects.select_related('user', 'department', 'manager').all():
    dept_name = emp.department.name if emp.department else 'No Department'
    manager_name = emp.manager.user.get_full_name() if emp.manager else 'No Manager'
    status = '✅ Active' if emp.status == 'ACTIVE' else f'❌ {emp.status}'
    print(f'  {emp.employee_id} | {emp.user.get_full_name()} | {emp.user.role}')
    print(f'    Position: {emp.position} | Department: {dept_name}')
    print(f'    Manager: {manager_name} | Status: {status}')
    print(f'    Salary: ${emp.salary:,.2f} | Hire Date: {emp.hire_date}')
    print()