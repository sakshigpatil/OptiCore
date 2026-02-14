#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/sakshi/vsCode/MajorProject/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.leaves.models import LeaveType, LeaveRequest
from apps.employees.models import Employee
from django.utils import timezone
from datetime import date, timedelta
import random

User = get_user_model()

def create_leave_data():
    print("Creating leave data...")
    
    # Create leave types
    leave_types = [
        {'name': 'Annual Leave', 'description': 'Yearly vacation leave', 'days_allowed_per_year': 25},
        {'name': 'Sick Leave', 'description': 'Medical leave for illness', 'days_allowed_per_year': 12},
        {'name': 'Personal Leave', 'description': 'Personal time off', 'days_allowed_per_year': 5},
        {'name': 'Maternity Leave', 'description': 'Maternity leave for new mothers', 'days_allowed_per_year': 180},
        {'name': 'Paternity Leave', 'description': 'Paternity leave for new fathers', 'days_allowed_per_year': 15},
        {'name': 'Emergency Leave', 'description': 'Emergency situations', 'days_allowed_per_year': 3},
    ]
    
    created_leave_types = []
    for leave_type_data in leave_types:
        leave_type, created = LeaveType.objects.get_or_create(
            name=leave_type_data['name'],
            defaults=leave_type_data
        )
        created_leave_types.append(leave_type)
        if created:
            print(f"Created leave type: {leave_type.name}")
    
    # Get all employees
    users = User.objects.filter(is_active=True)
    employees = []
    
    for user in users:
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': f'EMP{user.id:03d}',
                'hire_date': date.today() - timedelta(days=random.randint(30, 365))
            }
        )
        employees.append(employee)
    
    # Create some sample leave requests
    sample_requests = [
        {
            'leave_type': created_leave_types[0],  # Annual Leave
            'start_date': date(2025, 1, 15),
            'end_date': date(2025, 1, 19),
            'reason': 'Family vacation',
            'status': 'PENDING'
        },
        {
            'leave_type': created_leave_types[1],  # Sick Leave
            'start_date': date(2025, 11, 20),
            'end_date': date(2025, 11, 22),
            'reason': 'Medical appointment',
            'status': 'APPROVED'
        },
        {
            'leave_type': created_leave_types[2],  # Personal Leave
            'start_date': date(2025, 12, 5),
            'end_date': date(2025, 12, 5),
            'reason': 'Personal work',
            'status': 'PENDING'
        }
    ]
    
    # Create leave requests for Anita Singh
    anita_user = User.objects.get(username='anita.singh')
    anita_employee = Employee.objects.get(user=anita_user)
    
    for request_data in sample_requests:
        start_date = request_data['start_date']
        end_date = request_data['end_date']
        days_requested = (end_date - start_date).days + 1
        
        leave_request, created = LeaveRequest.objects.get_or_create(
            employee=anita_employee,
            leave_type=request_data['leave_type'],
            start_date=start_date,
            end_date=end_date,
            defaults={
                'days_requested': days_requested,
                'reason': request_data['reason'],
                'status': request_data['status']
            }
        )
        
        if created:
            print(f"Created leave request: {anita_employee.user.get_full_name()} - {request_data['leave_type'].name}")
    
    print("\nLeave data created successfully!")
    print(f"Total Leave Types: {LeaveType.objects.count()}")
    print(f"Total Leave Requests: {LeaveRequest.objects.count()}")
    print(f"Total Employees: {Employee.objects.count()}")

if __name__ == "__main__":
    create_leave_data()