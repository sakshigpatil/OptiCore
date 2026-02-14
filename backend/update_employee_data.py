#!/usr/bin/env python
"""
Script to update employee data with new user structure
"""

import os
import django
from datetime import date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee, Department

User = get_user_model()

def update_employee_data():
    print("Updating employee data with new user structure...")
    
    # First, clean up old users that are no longer needed
    old_usernames = ['admin', 'hr.manager', 'john.doe', 'jane.smith', 'mike.johnson']
    for username in old_usernames:
        try:
            user = User.objects.get(username=username)
            # Delete employee record if exists
            if hasattr(user, 'employee'):
                user.employee.delete()
                print(f"🗑️ Deleted employee record for: {username}")
            # Delete user
            user.delete()
            print(f"🗑️ Deleted old user: {username}")
        except User.DoesNotExist:
            continue
    
    # Create/Update departments
    departments_data = [
        {'name': 'Human Resources', 'description': 'HR Department - Employee management, recruitment, policies'},
        {'name': 'Engineering', 'description': 'Software Development and Technical Operations'},
        {'name': 'Marketing', 'description': 'Marketing and Business Development'},
        {'name': 'Sales', 'description': 'Sales and Customer Relations'},
    ]
    
    departments = {}
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        departments[dept.name] = dept
        if created:
            print(f"✅ Created department: {dept.name}")
        else:
            print(f"🔄 Updated department: {dept.name}")
    
    # Create employee records for new users
    employees_data = [
        {
            'username': 'priya.sharma',
            'employee_id': 'HR001',
            'department': 'Human Resources',
            'position': 'HR Director',
            'salary': Decimal('120000.00'),
            'hire_date': date(2020, 1, 15),
            'manager': None,  # HR Director has no manager
        },
        {
            'username': 'rajesh.kumar',
            'employee_id': 'ENG001', 
            'department': 'Engineering',
            'position': 'Engineering Manager',
            'salary': Decimal('95000.00'),
            'hire_date': date(2021, 3, 10),
            'manager': None,  # Will set after creating employees
        },
        {
            'username': 'arjun.patel',
            'employee_id': 'MKT001',
            'department': 'Marketing', 
            'position': 'Marketing Manager',
            'salary': Decimal('85000.00'),
            'hire_date': date(2021, 6, 20),
            'manager': None,  # Will set after creating employees
        },
        {
            'username': 'anita.singh',
            'employee_id': 'ENG002',
            'department': 'Engineering',
            'position': 'Senior Software Developer',
            'salary': Decimal('75000.00'),
            'hire_date': date(2022, 2, 1),
            'manager': 'rajesh.kumar',
        },
        {
            'username': 'vikram.mehta',
            'employee_id': 'MKT002',
            'department': 'Marketing',
            'position': 'Marketing Specialist', 
            'salary': Decimal('60000.00'),
            'hire_date': date(2022, 8, 15),
            'manager': 'arjun.patel',
        },
    ]
    
    # Create employees first (without manager relationships)
    created_employees = {}
    for emp_data in employees_data:
        try:
            user = User.objects.get(username=emp_data['username'])
            department = departments[emp_data['department']]
            
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': emp_data['employee_id'],
                    'department': department,
                    'position': emp_data['position'],
                    'salary': emp_data['salary'],
                    'hire_date': emp_data['hire_date'],
                    'status': 'ACTIVE',
                }
            )
            
            if not created:
                # Update existing employee
                employee.employee_id = emp_data['employee_id'] 
                employee.department = department
                employee.position = emp_data['position']
                employee.salary = emp_data['salary']
                employee.hire_date = emp_data['hire_date']
                employee.status = 'ACTIVE'
                employee.save()
            
            created_employees[emp_data['username']] = employee
            
            if created:
                print(f"✅ Created employee: {employee.employee_id} - {user.get_full_name()}")
            else:
                print(f"🔄 Updated employee: {employee.employee_id} - {user.get_full_name()}")
                
        except User.DoesNotExist:
            print(f"❌ User not found: {emp_data['username']}")
    
    # Now set manager relationships
    for emp_data in employees_data:
        if emp_data['manager']:
            try:
                employee = created_employees[emp_data['username']]
                manager = created_employees[emp_data['manager']]
                employee.manager = manager
                employee.save()
                print(f"👥 Set manager for {employee.user.get_full_name()}: {manager.user.get_full_name()}")
            except KeyError:
                print(f"❌ Could not set manager for {emp_data['username']}")
    
    # Set department heads
    try:
        # Set Priya as HR Department head
        hr_dept = departments['Human Resources']
        priya = created_employees['priya.sharma']
        hr_dept.head = priya
        hr_dept.save()
        print(f"🏢 Set HR Department head: {priya.user.get_full_name()}")
        
        # Set Rajesh as Engineering Department head
        eng_dept = departments['Engineering'] 
        rajesh = created_employees['rajesh.kumar']
        eng_dept.head = rajesh
        eng_dept.save()
        print(f"🏢 Set Engineering Department head: {rajesh.user.get_full_name()}")
        
        # Set Arjun as Marketing Department head
        mkt_dept = departments['Marketing']
        arjun = created_employees['arjun.patel']
        mkt_dept.head = arjun
        mkt_dept.save()
        print(f"🏢 Set Marketing Department head: {arjun.user.get_full_name()}")
        
    except KeyError as e:
        print(f"❌ Could not set department head: {e}")
    
    print("\n🎉 Employee data updated successfully!")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"Departments: {Department.objects.count()}")
    print(f"Employees: {Employee.objects.count()}")
    print(f"Users: {User.objects.count()}")

if __name__ == "__main__":
    update_employee_data()