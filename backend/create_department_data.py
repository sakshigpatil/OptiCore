#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/sakshi/vsCode/MajorProject/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from apps.employees.models import Department, Employee
from django.contrib.auth import get_user_model

User = get_user_model()

def create_departments():
    print("Creating sample departments...")
    
    # Sample department data
    departments_data = [
        {
            'name': 'Engineering',
            'description': 'Software development and technical operations'
        },
        {
            'name': 'Human Resources',
            'description': 'Employee management and organizational development'
        },
        {
            'name': 'Marketing',
            'description': 'Brand promotion and customer engagement'
        },
        {
            'name': 'Finance',
            'description': 'Financial planning and accounting'
        }
    ]
    
    created_departments = []
    
    for dept_data in departments_data:
        department, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={
                'description': dept_data['description'],
                'is_active': True
            }
        )
        created_departments.append(department)
        
        if created:
            print(f"Created department: {department.name}")
        else:
            print(f"Department already exists: {department.name}")
    
    # Assign some employees to departments if they exist
    employees = Employee.objects.all()[:4]
    
    for i, employee in enumerate(employees):
        if i < len(created_departments):
            department = created_departments[i % len(created_departments)]
            if not employee.department:
                employee.department = department
                employee.save()
                print(f"Assigned {employee.user.get_full_name()} to {department.name}")
    
    print(f"\nTotal departments: {Department.objects.filter(is_active=True).count()}")
    
    # Show department stats
    for dept in Department.objects.filter(is_active=True):
        employee_count = dept.employee_set.filter(status='ACTIVE').count()
        head_name = dept.head.user.get_full_name() if dept.head else 'None'
        print(f"{dept.name}: {employee_count} employees, Head: {head_name}")

if __name__ == "__main__":
    create_departments()