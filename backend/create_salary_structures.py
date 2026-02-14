#!/usr/bin/env python
"""
Create salary structures for all employees
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.payroll.models import SalaryStructure
from apps.employees.models import Employee

User = get_user_model()

def create_salary_structures():
    print("Creating salary structures for all employees...")
    
    employees = Employee.objects.all()
    
    for emp in employees:
        # Calculate salary components based on employee's base salary
        basic_salary = emp.salary
        
        salary_structure, created = SalaryStructure.objects.get_or_create(
            employee=emp.user,
            defaults={
                'salary_type': 'MONTHLY',
                'basic': basic_salary,
                'hra_percent': 20,  # 20% of basic as HRA
                'hra_fixed': 0,
                'conveyance': Decimal('2000'),  # Fixed conveyance
                'medical_allowance': Decimal('1500'),  # Fixed medical allowance
                'special_allowance': Decimal('3000'),  # Fixed special allowance
                'other_allowances': Decimal('1000'),  # Other allowances
                'pf_percent': 12,  # 12% PF deduction
                'esi_percent': 0.75,  # 0.75% ESI
                'professional_tax': Decimal('200'),  # Fixed professional tax
                'bonus_eligible': True,
                'overtime_rate': Decimal('1.5'),
                'annual_ctc': basic_salary * 12,  # Annual CTC
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created salary structure for {emp.user.get_full_name()} - Basic: ${basic_salary}")
        else:
            print(f"🔄 Salary structure already exists for {emp.user.get_full_name()}")
    
    print("\n🎉 Salary structures created successfully!")
    print("\n📊 Summary:")
    structures = SalaryStructure.objects.all()
    total_ctc = sum(s.annual_ctc for s in structures)
    print(f"Total Salary Structures: {structures.count()}")
    print(f"Total Annual CTC: ${total_ctc:,.2f}")
    print(f"Average Annual CTC: ${total_ctc/structures.count():,.2f}")

if __name__ == "__main__":
    create_salary_structures()