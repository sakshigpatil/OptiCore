#!/usr/bin/env python
"""
Seed script to populate the database with sample data
Run with: python manage.py shell < scripts/seed_data.py
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Department, Employee
from apps.leaves.models import LeaveType, LeaveRequest
# from apps.payroll.models import PayrollRecord  # Commented out as not used
from apps.attendance.models import Attendance
from apps.projects.models import Project, Task
from apps.notifications.models import Notification

User = get_user_model()

def create_sample_data():
    print("Creating sample data...")
    
    # Create departments
    departments = [
        {'name': 'Engineering', 'description': 'Software Development and Engineering'},
        {'name': 'Human Resources', 'description': 'HR and People Operations'},
        {'name': 'Marketing', 'description': 'Marketing and Sales'},
        {'name': 'Finance', 'description': 'Finance and Accounting'},
        {'name': 'Operations', 'description': 'Business Operations'},
    ]
    
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        if created:
            print(f"Created department: {dept.name}")
    
    # Create users and employees
    users_data = [
        {
            'username': 'admin', 'email': 'admin@hrms.com',
            'first_name': 'System', 'last_name': 'Administrator',
            'role': 'ADMIN_HR', 'is_staff': True, 'is_superuser': True
        },
        {
            'username': 'hr.manager', 'email': 'hr@hrms.com',
            'first_name': 'HR', 'last_name': 'Manager', 'role': 'ADMIN_HR'
        },
        {
            'username': 'john.doe', 'email': 'john.doe@hrms.com',
            'first_name': 'John', 'last_name': 'Doe', 'role': 'MANAGER'
        },
        {
            'username': 'jane.smith', 'email': 'jane.smith@hrms.com',
            'first_name': 'Jane', 'last_name': 'Smith', 'role': 'EMPLOYEE'
        },
        {
            'username': 'mike.johnson', 'email': 'mike.johnson@hrms.com',
            'first_name': 'Mike', 'last_name': 'Johnson', 'role': 'EMPLOYEE'
        },
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
            }
        )
        if created:
            user.set_password('password123')  # Default password for demo
            user.save()
            print(f"Created user: {user.username}")
    
    # Create employee profiles
    employees_data = [
        {
            'user': User.objects.get(username='hr.manager'),
            'employee_id': 'EMP001', 'position': 'HR Manager',
            'department': Department.objects.get(name='Human Resources'),
            'salary': Decimal('75000.00')
        },
        {
            'user': User.objects.get(username='john.doe'),
            'employee_id': 'EMP002', 'position': 'Engineering Manager',
            'department': Department.objects.get(name='Engineering'),
            'salary': Decimal('90000.00')
        },
        {
            'user': User.objects.get(username='jane.smith'),
            'employee_id': 'EMP003', 'position': 'Senior Developer',
            'department': Department.objects.get(name='Engineering'),
            'salary': Decimal('80000.00'),
            'manager': None  # Will be set after creation
        },
        {
            'user': User.objects.get(username='mike.johnson'),
            'employee_id': 'EMP004', 'position': 'Marketing Specialist',
            'department': Department.objects.get(name='Marketing'),
            'salary': Decimal('55000.00')
        },
    ]
    
    for emp_data in employees_data:
        emp, created = Employee.objects.get_or_create(
            user=emp_data['user'],
            defaults={
                'employee_id': emp_data['employee_id'],
                'position': emp_data['position'],
                'department': emp_data['department'],
                'salary': emp_data['salary'],
                'hire_date': date.today() - timedelta(days=365),
                'address': '123 Main St, City, State 12345',
                'emergency_contact_name': 'Emergency Contact',
                'emergency_contact_phone': '+1234567890'
            }
        )
        if created:
            print(f"Created employee: {emp.employee_id}")
    
    # Set manager relationships
    jane = Employee.objects.get(employee_id='EMP003')
    john = Employee.objects.get(employee_id='EMP002')
    jane.manager = john
    jane.save()
    
    # Create leave types
    leave_types = [
        {'name': 'Annual Leave', 'description': 'Annual vacation leave', 'days_allowed_per_year': 25},
        {'name': 'Sick Leave', 'description': 'Medical leave', 'days_allowed_per_year': 10},
        {'name': 'Maternity Leave', 'description': 'Maternity leave', 'days_allowed_per_year': 90},
        {'name': 'Personal Leave', 'description': 'Personal time off', 'days_allowed_per_year': 5},
    ]
    
    for leave_data in leave_types:
        leave_type, created = LeaveType.objects.get_or_create(
            name=leave_data['name'],
            defaults=leave_data
        )
        if created:
            print(f"Created leave type: {leave_type.name}")
    
    # Create sample projects
    projects_data = [
        {
            'name': 'HRMS Development',
            'description': 'Development of HR Management System',
            'manager': Employee.objects.get(employee_id='EMP002'),
            'start_date': date.today() - timedelta(days=60),
            'end_date': date.today() + timedelta(days=120),
            'status': 'IN_PROGRESS'
        },
        {
            'name': 'Marketing Campaign Q1',
            'description': 'Q1 marketing campaign planning and execution',
            'manager': Employee.objects.get(employee_id='EMP004'),
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today() + timedelta(days=60),
            'status': 'PLANNING'
        }
    ]
    
    for proj_data in projects_data:
        project, created = Project.objects.get_or_create(
            name=proj_data['name'],
            defaults=proj_data
        )
        if created:
            print(f"Created project: {project.name}")
    
    # Create sample tasks
    hrms_project = Project.objects.get(name='HRMS Development')
    jane_emp = Employee.objects.get(employee_id='EMP003')
    
    tasks_data = [
        {
            'title': 'Setup Authentication System',
            'description': 'Implement JWT authentication',
            'project': hrms_project,
            'assigned_to': jane_emp,
            'created_by': john,
            'priority': 'HIGH',
            'status': 'IN_PROGRESS',
            'due_date': date.today() + timedelta(days=7)
        },
        {
            'title': 'Design Database Schema',
            'description': 'Create database models and relationships',
            'project': hrms_project,
            'assigned_to': jane_emp,
            'created_by': john,
            'priority': 'MEDIUM',
            'status': 'COMPLETED',
            'due_date': date.today() - timedelta(days=5)
        }
    ]
    
    for task_data in tasks_data:
        task, created = Task.objects.get_or_create(
            title=task_data['title'],
            project=task_data['project'],
            defaults=task_data
        )
        if created:
            print(f"Created task: {task.title}")
    
    # Create sample attendance records
    employees = Employee.objects.all()
    for employee in employees:
        for i in range(30):  # Last 30 days
            date_record = date.today() - timedelta(days=i)
            if date_record.weekday() < 5:  # Monday to Friday
                attendance, created = Attendance.objects.get_or_create(
                    employee=employee,
                    date=date_record,
                    defaults={
                        'clock_in': datetime.strptime('09:00', '%H:%M').time(),
                        'clock_out': datetime.strptime('17:30', '%H:%M').time(),
                        'status': 'PRESENT',
                        'hours_worked': Decimal('8.5')
                    }
                )
                if created and i < 5:  # Only print recent ones
                    print(f"Created attendance for {employee.user.get_full_name()} on {date_record}")
    
    # Create sample notifications
    hr_user = User.objects.get(username='hr.manager')
    jane_user = User.objects.get(username='jane.smith')
    
    notifications_data = [
        {
            'recipient': jane_user,
            'sender': hr_user,
            'title': 'Welcome to HRMS',
            'message': 'Welcome to the HR Management System!',
            'notification_type': 'INFO'
        },
        {
            'recipient': jane_user,
            'title': 'Task Assignment',
            'message': 'You have been assigned a new task: Setup Authentication System',
            'notification_type': 'TASK_ASSIGNED'
        }
    ]
    
    for notif_data in notifications_data:
        notification, created = Notification.objects.get_or_create(
            recipient=notif_data['recipient'],
            title=notif_data['title'],
            defaults=notif_data
        )
        if created:
            print(f"Created notification: {notification.title}")
    
    print("Sample data creation completed!")

if __name__ == "__main__":
    create_sample_data()