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
from apps.payroll.models import PayrollRun, Payslip, SalaryStructure
from django.utils import timezone
from decimal import Decimal
import random

User = get_user_model()

def create_payroll_data():
    print("Creating payroll data...")
    
    # Create payroll runs for past 6 months
    current_date = timezone.now().date()
    
    for i in range(6):
        # Calculate month and year going backwards
        if current_date.month - i > 0:
            month = current_date.month - i
            year = current_date.year
        else:
            month = 12 + (current_date.month - i)
            year = current_date.year - 1
        
        # Check if payroll run already exists
        run, created = PayrollRun.objects.get_or_create(
            year=year,
            month=month,
            defaults={
                'processed': True,
            }
        )
        
        if created:
            print(f"Created payroll run for {month}/{year}")
        
        # Create payslips for all active employees
        employees = User.objects.filter(is_active=True)
        
        for employee in employees:
            # Skip if payslip already exists
            if Payslip.objects.filter(payroll_run=run, employee=employee).exists():
                continue
                
            # Get or create salary structure
            salary_structure, _ = SalaryStructure.objects.get_or_create(
                employee=employee,
                defaults={
                    'basic': Decimal('50000.00'),
                    'hra_percent': Decimal('40.00'),
                    'conveyance': Decimal('2000.00'),
                    'other_allowances': Decimal('5000.00'),
                    'pf_percent': Decimal('12.00'),
                    'professional_tax': Decimal('200.00'),
                    'effective_from': timezone.now().date(),
                    'is_active': True
                }
            )
            
            # Calculate salary components
            basic = salary_structure.basic
            hra = salary_structure.get_hra_amount()
            conveyance = salary_structure.conveyance
            other_allowances = salary_structure.other_allowances
            
            gross_salary = basic + hra + conveyance + other_allowances
            
            # Calculate deductions
            pf = basic * (salary_structure.pf_percent / 100)
            professional_tax = salary_structure.professional_tax
            income_tax = gross_salary * Decimal('0.10')  # 10% tax rate
            
            total_deductions_amount = pf + professional_tax + income_tax
            net_salary = gross_salary - total_deductions_amount
            
            # Add some randomness to attendance-based calculations
            attendance_factor = random.uniform(0.95, 1.0)  # 95% to 100% attendance
            gross_salary = gross_salary * Decimal(str(attendance_factor))
            net_salary = net_salary * Decimal(str(attendance_factor))
            
            # Create payslip
            payslip = Payslip.objects.create(
                payroll_run=run,
                employee=employee,
                gross_salary=gross_salary.quantize(Decimal('0.01')),
                total_deductions=total_deductions_amount.quantize(Decimal('0.01')),
                net_salary=net_salary.quantize(Decimal('0.01')),
                components={
                    'basic': float(basic),
                    'hra': float(hra),
                    'conveyance': float(conveyance),
                    'other_allowances': float(other_allowances),
                    'gross': float(gross_salary),
                    'pf': float(pf),
                    'professional_tax': float(professional_tax),
                    'tax': float(income_tax),
                }
            )
            
            print(f"Created payslip for {employee.username} - {month}/{year}")
    
    print("\nPayroll data created successfully!")
    print(f"Total Payroll Runs: {PayrollRun.objects.count()}")
    print(f"Total Payslips: {Payslip.objects.count()}")
    print(f"Total Salary Structures: {SalaryStructure.objects.count()}")

if __name__ == "__main__":
    create_payroll_data()