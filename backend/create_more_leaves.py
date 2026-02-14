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
from datetime import date, timedelta

User = get_user_model()

def create_additional_leave_requests():
    print("Creating additional leave requests...")
    
    # Get leave types
    annual_leave = LeaveType.objects.get(name='Annual Leave')
    sick_leave = LeaveType.objects.get(name='Sick Leave')
    personal_leave = LeaveType.objects.get(name='Personal Leave')
    
    # Get users to create requests for
    users = User.objects.filter(is_active=True)[:4]  # Get first 4 users
    
    sample_requests = [
        {
            'leave_type': annual_leave,
            'start_date': date(2025, 1, 15),
            'end_date': date(2025, 1, 19),
            'reason': 'Wedding ceremony in family',
            'status': 'PENDING'
        },
        {
            'leave_type': sick_leave,
            'start_date': date(2025, 1, 8),
            'end_date': date(2025, 1, 10),
            'reason': 'Medical checkup and recovery',
            'status': 'PENDING'
        },
        {
            'leave_type': personal_leave,
            'start_date': date(2025, 1, 22),
            'end_date': date(2025, 1, 22),
            'reason': 'House shifting',
            'status': 'PENDING'
        }
    ]
    
    for i, user in enumerate(users[:3]):  # Create requests for first 3 users
        try:
            employee = Employee.objects.get(user=user)
            request_data = sample_requests[i % len(sample_requests)]
            
            # Calculate days requested
            start_date = request_data['start_date']
            end_date = request_data['end_date']
            days_requested = (end_date - start_date).days + 1
            
            # Check if this request already exists
            existing_request = LeaveRequest.objects.filter(
                employee=employee,
                leave_type=request_data['leave_type'],
                start_date=start_date,
                end_date=end_date
            ).first()
            
            if not existing_request:
                leave_request = LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=request_data['leave_type'],
                    start_date=start_date,
                    end_date=end_date,
                    days_requested=days_requested,
                    reason=request_data['reason'],
                    status=request_data['status']
                )
                print(f"Created leave request: {employee.user.get_full_name()} - {request_data['leave_type'].name}")
            else:
                print(f"Request already exists for {employee.user.get_full_name()}")
        
        except Employee.DoesNotExist:
            print(f"No employee profile for user: {user.username}")
    
    print(f"\nTotal pending leave requests: {LeaveRequest.objects.filter(status='PENDING').count()}")

if __name__ == "__main__":
    create_additional_leave_requests()