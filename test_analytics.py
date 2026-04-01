#!/usr/bin/env python
"""
Test script for Phase 4 Analytics & Export Features
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
sys.path.insert(0, '/home/sakshi/vsCode/MajorProject/backend')
django.setup()

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from apps.employees.models import Employee, Department
from apps.analytics.views import get_user_permissions

def test_analytics_api():
    """Test the analytics API endpoints"""
    print("🧪 Testing Analytics API...")

    client = Client()

    # Create test user
    try:
        user = User.objects.create_user(
            username='test_hr',
            email='test@hr.com',
            password='testpass123',
            first_name='Test',
            last_name='HR'
        )
        user.role = 'ADMIN_HR'
        user.save()

        # Create test department
        dept = Department.objects.create(
            name='Engineering',
            description='Engineering Department'
        )

        # Create test employee
        employee = Employee.objects.create(
            user=user,
            department=dept,
            position='HR Manager',
            salary=75000
        )

        print("✅ Test data created")

        # Test login
        login_response = client.post('/api/v1/auth/login/', {
            'username': 'test_hr',
            'password': 'testpass123'
        })
        print(f"Login response: {login_response.status_code}")

        # Test analytics dashboard endpoint
        response = client.get('/api/v1/analytics/dashboard/')
        print(f"Analytics dashboard response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics data retrieved successfully")
            print(f"Employee stats: {data.get('employee_stats', {})}")
        else:
            print(f"❌ Analytics API failed: {response.content}")

        # Test export endpoints
        export_response = client.get('/api/v1/analytics/export/employees/?format=csv')
        print(f"Export employees response: {export_response.status_code}")

        if export_response.status_code == 200:
            print("✅ Employee export successful")
        else:
            print(f"❌ Employee export failed: {export_response.content}")

        # Cleanup
        employee.delete()
        dept.delete()
        user.delete()

        print("🧪 Analytics API tests completed")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == '__main__':
    test_analytics_api()