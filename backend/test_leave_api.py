#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append('/home/sakshi/vsCode/MajorProject/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.leaves.models import LeaveRequest

User = get_user_model()

def test_leave_api():
    print("Testing Leave API...")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@hrms.com',
            'first_name': 'HR',
            'last_name': 'Administrator',
            'is_staff': True,
            'is_superuser': True,
            'role': 'ADMIN_HR',
            'is_approved': True,
            'approval_status': 'APPROVED'
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created admin user")
    else:
        # Update existing admin user to be approved
        admin_user.is_approved = True
        admin_user.approval_status = 'APPROVED'
        admin_user.role = 'ADMIN_HR'
        admin_user.save()
        print("Updated admin user approval status")
    
    # Create admin employee profile if not exists
    admin_employee, created = Employee.objects.get_or_create(
        user=admin_user,
        defaults={
            'employee_id': 'ADM001',
            'hire_date': '2024-01-01',
            'position': 'HR Administrator',
            'salary': 80000.00
        }
    )
    
    # Login to get token
    login_data = {
        'email': 'admin@hrms.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/v1/auth/login/', 
                               json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access')
            print("Login successful, got token")
            
            # Test leave requests endpoint
            headers = {'Authorization': f'Bearer {token}'}
            
            leave_response = requests.get(
                'http://localhost:8000/api/v1/leaves/leave-requests/', 
                headers=headers
            )
            
            if leave_response.status_code == 200:
                leave_data = leave_response.json()
                print(f"✅ Leave requests API working! Found {len(leave_data)} requests")
                
                # Print first request for verification
                if leave_data:
                    first_request = leave_data[0]
                    print(f"Sample request: {first_request.get('employee_name')} - {first_request.get('leave_type_name')}")
            else:
                print(f"❌ Leave requests API failed: {leave_response.status_code}")
                print(leave_response.text)
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

    # Print some database stats
    print(f"\nDatabase stats:")
    print(f"Users: {User.objects.count()}")
    print(f"Employees: {Employee.objects.count()}")
    print(f"Leave Requests: {LeaveRequest.objects.count()}")

if __name__ == "__main__":
    test_leave_api()