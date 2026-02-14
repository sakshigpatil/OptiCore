#!/usr/bin/env python
"""
Create sample employee and department data
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee, Department

User = get_user_model()

def create_employee_data():
    print("Creating employee and department data...")
    
    # Create departments
    departments_data = [
        {'name': 'Engineering', 'description': 'Software Development and Engineering'},
        {'name': 'Human Resources', 'description': 'HR and People Operations'},
        {'name': 'Marketing', 'description': 'Marketing and Sales'},
        {'name': 'Finance', 'description': 'Finance and Accounting'},
        {'name': 'Operations', 'description': 'Business Operations'},
    ]
    
    created_departments = []
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        created_departments.append(dept)
        if created:
            print(f"✅ Created department: {dept.name}")
        else:
            print(f"🔄 Department already exists: {dept.name}")
    
    # Create employee profiles
    employees_data = [
        {
            'username': 'admin',
            'employee_id': 'EMP000',
            'position': 'System Administrator',
            'department': 'Human Resources',
            'salary': Decimal('120000.00'),
            'hire_date': date(2024, 1, 1)
        },
        {
            'username': 'hr.manager',
            'employee_id': 'EMP001',
            'position': 'HR Manager',
            'department': 'Human Resources',
            'salary': Decimal('85000.00'),
            'hire_date': date(2024, 2, 1)
        },
        {
            'username': 'john.doe',
            'employee_id': 'EMP002',
            'position': 'Engineering Manager',
            'department': 'Engineering',
            'salary': Decimal('95000.00'),
            'hire_date': date(2024, 1, 15)
        },
        {
            'username': 'jane.smith',
            'employee_id': 'EMP003',
            'position': 'Senior Software Engineer',
            'department': 'Engineering',
            'salary': Decimal('80000.00'),
            'hire_date': date(2024, 3, 1)
        },
        {
            'username': 'mike.johnson',
            'employee_id': 'EMP004',
            'position': 'Marketing Specialist',
            'department': 'Marketing',
            'salary': Decimal('60000.00'),
            'hire_date': date(2024, 4, 1)
        },
    ]
    
    created_employees = []
    for emp_data in employees_data:
        try:
            user = User.objects.get(username=emp_data['username'])
            department = Department.objects.get(name=emp_data['department'])
            
            emp, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': emp_data['employee_id'],
                    'position': emp_data['position'],
                    'department': department,
                    'salary': emp_data['salary'],
                    'hire_date': emp_data['hire_date'],
                    'address': '123 Main St, City, State 12345',
                    'emergency_contact_name': f"{user.first_name} Emergency Contact",
                    'emergency_contact_phone': '+1234567890'
                }
            )
            created_employees.append(emp)
            if created:
                print(f"✅ Created employee: {emp.employee_id} - {emp.user.get_full_name()}")
            else:
                print(f"🔄 Employee already exists: {emp.employee_id} - {emp.user.get_full_name()}")
        except User.DoesNotExist:
            print(f"❌ User {emp_data['username']} not found")
        except Department.DoesNotExist:
            print(f"❌ Department {emp_data['department']} not found")
    
    # Set manager relationships
    try:
        jane_emp = Employee.objects.get(employee_id='EMP003')
        john_emp = Employee.objects.get(employee_id='EMP002')
        jane_emp.manager = john_emp
        jane_emp.save()
        print(f"✅ Set manager: {jane_emp.user.get_full_name()} reports to {john_emp.user.get_full_name()}")
        
        # Set department heads
        hr_dept = Department.objects.get(name='Human Resources')
        eng_dept = Department.objects.get(name='Engineering')
        mkt_dept = Department.objects.get(name='Marketing')
        
        hr_manager = Employee.objects.get(employee_id='EMP001')
        eng_manager = Employee.objects.get(employee_id='EMP002')
        mkt_emp = Employee.objects.get(employee_id='EMP004')
        
        hr_dept.head = hr_manager
        hr_dept.save()
        
        eng_dept.head = eng_manager
        eng_dept.save()
        
        mkt_dept.head = mkt_emp
        mkt_dept.save()
        
        print(f"✅ Set department heads")
        
    except Employee.DoesNotExist as e:
        print(f"❌ Error setting relationships: {e}")
    
    print("\n🎉 Employee and department data created successfully!")

if __name__ == "__main__":
    create_employee_data()