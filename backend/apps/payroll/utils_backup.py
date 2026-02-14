from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from django.utils import timezone
from calendar import monthrange
import datetime
from .models import quant, EmployeeLoan, Bonus, Reimbursement, PayrollComponent

def calculate_payslip_for_employee(salary_structure, attendance_summary=None, policy=None, payroll_run=None):
    """
    Comprehensive payroll calculation with attendance integration, statutory compliance,
    bonuses, loans, reimbursements, and configurable components.
    
    salary_structure: SalaryStructure instance
    attendance_summary: dict with 'working_days_in_month', 'present_days', 'overtime_hours', 'lop_days'
    policy: dict to override tax rates, statutory limits, etc.
    payroll_run: PayrollRun instance for bonus/reimbursement processing
    
    Returns: dict with gross, deductions, net, components, details
    """
    if policy is None:
        policy = {}
    
    if attendance_summary is None:
        attendance_summary = {
            'working_days_in_month': 30,
            'present_days': 30,
            'overtime_hours': 0,
            'lop_days': 0
        }

    # Get working days in month
    working_days = attendance_summary.get('working_days_in_month', 30)
    present_days = attendance_summary.get('present_days', working_days)
    overtime_hours = attendance_summary.get('overtime_hours', 0)
    lop_days = attendance_summary.get('lop_days', 0)
    
    # Basic salary calculations
    basic = Decimal(salary_structure.basic)
    
    # Handle different salary types
    if salary_structure.salary_type == 'HOURLY':
        # For hourly employees, calculate based on hours worked
        standard_hours_per_day = 8
        total_standard_hours = working_days * standard_hours_per_day
        actual_hours = present_days * standard_hours_per_day
        basic = (basic * actual_hours / total_standard_hours) if total_standard_hours > 0 else basic
    elif salary_structure.salary_type == 'DAILY':
        # For daily wage employees
        basic = (basic * present_days / working_days) if working_days > 0 else basic
    elif salary_structure.salary_type == 'MONTHLY':
        # Adjust for LOP (Loss of Pay)
        if lop_days > 0:
            basic = basic - (basic * lop_days / working_days)
    
    basic = quant(basic)
    
    # Calculate allowances
    hra = quant(salary_structure.get_hra_amount())
    medical_allowance = quant(salary_structure.medical_allowance)
    special_allowance = quant(salary_structure.special_allowance)
    conveyance = quant(salary_structure.conveyance)
    other_allowances = quant(salary_structure.other_allowances)
    
    # Adjust allowances for LOP if monthly salary
    if salary_structure.salary_type == 'MONTHLY' and lop_days > 0:
        lop_factor = Decimal(1) - (Decimal(lop_days) / Decimal(working_days))
        hra = hra * lop_factor
        medical_allowance = medical_allowance * lop_factor
        special_allowance = special_allowance * lop_factor
        conveyance = conveyance * lop_factor
        other_allowances = other_allowances * lop_factor  # Calculate overtime pay\n    overtime_pay = Decimal(0)\n    if overtime_hours > 0 and salary_structure.salary_type != 'CONTRACT':\n        hourly_rate = basic / (working_days * 8)  # Assuming 8 hours per day\n        overtime_rate = salary_structure.overtime_rate\n        overtime_pay = quant(hourly_rate * Decimal(overtime_hours) * overtime_rate)\n    \n    # Calculate bonuses for this period\n    bonus_amount = Decimal(0)\n    if payroll_run and salary_structure.bonus_eligible:\n        bonuses = Bonus.objects.filter(\n            employee=salary_structure.employee,\n            applicable_month=payroll_run.month,\n            applicable_year=payroll_run.year,\n            is_processed=False\n        )\n        for bonus in bonuses:\n            bonus_amount += quant(bonus.calculate_amount(basic))\n    \n    # Calculate reimbursements\n    reimbursement_amount = Decimal(0)\n    if payroll_run:\n        approved_reimbursements = Reimbursement.objects.filter(\n            employee=salary_structure.employee,\n            status='APPROVED',\n            paid_in_payroll__isnull=True\n        )\n        for reimbursement in approved_reimbursements:\n            reimbursement_amount += quant(reimbursement.amount)\n    \n    # Calculate gross salary\n    gross_salary = (\n        basic + hra + medical_allowance + special_allowance + \n        conveyance + other_allowances + overtime_pay + bonus_amount + reimbursement_amount\n    )\n    \n    # === STATUTORY DEDUCTIONS ===\n    \n    # Provident Fund (PF) - 12% of basic, max limit as per policy\n    pf_percent = Decimal(salary_structure.pf_percent) / Decimal(100)\n    pf_basic = min(basic, Decimal(policy.get('pf_salary_limit', 15000)))  # PF limit\n    pf_deduction = quant(pf_basic * pf_percent)\n    \n    # Employee State Insurance (ESI) - 0.75% if salary <= ESI limit\n    esi_deduction = Decimal(0)\n    esi_limit = Decimal(policy.get('esi_salary_limit', 21000))\n    if gross_salary <= esi_limit:\n        esi_percent = Decimal(salary_structure.esi_percent) / Decimal(100)\n        esi_deduction = quant(gross_salary * esi_percent)\n    \n    # Professional Tax (PT) - State-specific slabs\n    professional_tax = calculate_professional_tax(gross_salary, policy)\n    \n    # Income Tax (TDS) - Based on annual projections\n    income_tax = calculate_income_tax(basic, gross_salary, salary_structure, policy)\n    \n    # === OTHER DEDUCTIONS ===\n    \n    # Loan EMI deductions\n    loan_deduction = Decimal(0)\n    if payroll_run:\n        active_loans = EmployeeLoan.objects.filter(\n            employee=salary_structure.employee,\n            status='ACTIVE',\n            remaining_amount__gt=0\n        )\n        for loan in active_loans:\n            emi_amount = min(loan.emi_amount, loan.remaining_amount)\n            loan_deduction += quant(emi_amount)\n    \n    # Custom deduction components\n    custom_deductions = Decimal(0)\n    deduction_components = PayrollComponent.objects.filter(\n        component_type='DEDUCTION',\n        is_active=True\n    )\n    \n    deduction_details = {}\n    for component in deduction_components:\n        if component.min_salary_threshold and gross_salary < component.min_salary_threshold:\n            continue\n        if component.max_salary_threshold and gross_salary > component.max_salary_threshold:\n            continue\n            \n        if component.calculation_type == 'FIXED':\n            deduction_amount = component.default_value\n        elif component.calculation_type == 'PERCENTAGE':\n            deduction_amount = (basic * component.default_value / 100)\n        elif component.calculation_type == 'PERCENTAGE_GROSS':\n            deduction_amount = (gross_salary * component.default_value / 100)\n        else:\n            deduction_amount = 0\n            \n        deduction_amount = quant(deduction_amount)\n        custom_deductions += deduction_amount\n        deduction_details[component.name.lower().replace(' ', '_')] = float(deduction_amount)\n    \n    # Total deductions\n    total_deductions = (\n        pf_deduction + esi_deduction + professional_tax + \n        income_tax + loan_deduction + custom_deductions\n    )\n    \n    # Net salary\n    net_salary = quant(gross_salary - total_deductions)\n    \n    # Detailed components breakdown\n    components = {\n        # Earnings\n        'basic': float(basic),\n        'hra': float(hra),\n        'medical_allowance': float(medical_allowance),\n        'special_allowance': float(special_allowance),\n        'conveyance': float(conveyance),\n        'other_allowances': float(other_allowances),\n        'overtime_pay': float(overtime_pay),\n        'bonus': float(bonus_amount),\n        'reimbursements': float(reimbursement_amount),\n        'gross_salary': float(gross_salary),\n        \n        # Deductions\n        'pf_deduction': float(pf_deduction),\n        'esi_deduction': float(esi_deduction),\n        'professional_tax': float(professional_tax),\n        'income_tax': float(income_tax),\n        'loan_deduction': float(loan_deduction),\n        'total_deductions': float(total_deductions),\n        \n        # Net\n        'net_salary': float(net_salary),\n        \n        # Attendance details\n        'working_days': working_days,\n        'present_days': present_days,\n        'lop_days': lop_days,\n        'overtime_hours': overtime_hours,\n    }\n    \n    # Add custom deduction details\n    components.update(deduction_details)\n    \n    return {\n        'gross_salary': gross_salary,\n        'total_deductions': total_deductions,\n        'net_salary': net_salary,\n        'components': components,\n        'attendance_summary': attendance_summary\n    }\n\n\ndef calculate_professional_tax(gross_salary, policy=None):\n    \"\"\"\n    Calculate Professional Tax based on salary slabs.\n    This is a simplified version - implement state-specific PT slabs.\n    \"\"\"\n    if policy is None:\n        policy = {}\n    \n    # Default PT slabs (can be overridden in policy)\n    pt_slabs = policy.get('pt_slabs', [\n        {'min': 0, 'max': 10000, 'tax': 0},\n        {'min': 10001, 'max': 15000, 'tax': 150},\n        {'min': 15001, 'max': 25000, 'tax': 200},\n        {'min': 25001, 'max': float('inf'), 'tax': 300},\n    ])\n    \n    for slab in pt_slabs:\n        if slab['min'] <= gross_salary <= slab['max']:\n            return Decimal(slab['tax'])\n    \n    return Decimal(0)\n\n\ndef calculate_income_tax(basic_salary, gross_salary, salary_structure, policy=None):\n    \"\"\"\n    Calculate monthly income tax based on annual projections.\n    This is a simplified version - implement proper tax calculations with exemptions.\n    \"\"\"\n    if policy is None:\n        policy = {}\n    \n    # Annual gross projection\n    annual_gross = gross_salary * 12\n    \n    # Tax slabs (FY 2024-25 - New Tax Regime)\n    tax_slabs = policy.get('tax_slabs', [\n        {'min': 0, 'max': 300000, 'rate': 0},\n        {'min': 300001, 'max': 700000, 'rate': 5},\n        {'min': 700001, 'max': 1000000, 'rate': 10},\n        {'min': 1000001, 'max': 1200000, 'rate': 15},\n        {'min': 1200001, 'max': 1500000, 'rate': 20},\n        {'min': 1500001, 'max': float('inf'), 'rate': 30},\n    ])\n    \n    annual_tax = Decimal(0)\n    for slab in tax_slabs:\n        if annual_gross > slab['min']:\n            taxable_amount = min(annual_gross, slab['max']) - slab['min'] + 1\n            if taxable_amount > 0:\n                annual_tax += (taxable_amount * Decimal(slab['rate']) / 100)\n    \n    # Monthly tax deduction\n    monthly_tax = annual_tax / 12\n    return quant(monthly_tax)\n\n\ndef get_attendance_summary_for_employee(employee, year, month):\n    \"\"\"\n    Get attendance summary for payroll calculation.\n    Integrates with attendance module.\n    \"\"\"\n    try:\n        from apps.attendance.models import AttendanceRecord\n        \n        # Get working days in month\n        _, last_day = monthrange(year, month)\n        working_days = last_day  # Simplified - should exclude weekends/holidays\n        \n        # Get attendance records for the month\n        attendance_records = AttendanceRecord.objects.filter(\n            employee__user=employee,\n            clock_in__year=year,\n            clock_in__month=month\n        )\n        \n        present_days = attendance_records.filter(clock_out__isnull=False).count()\n        total_overtime = attendance_records.aggregate(\n            total_ot=Sum('overtime_hours')\n        )['total_ot'] or 0\n        \n        # Calculate LOP days\n        lop_days = max(0, working_days - present_days)\n        \n        return {\n            'working_days_in_month': working_days,\n            'present_days': present_days,\n            'overtime_hours': float(total_overtime),\n            'lop_days': lop_days\n        }\n        \n    except ImportError:\n        # Attendance module not available\n        return {\n            'working_days_in_month': 30,\n            'present_days': 30,\n            'overtime_hours': 0,\n            'lop_days': 0\n        }\n\n\ndef generate_bank_transfer_file(payroll_run):\n    \"\"\"\n    Generate bank transfer file for bulk salary payments.\n    Returns CSV format data for bank upload.\n    \"\"\"\n    from .models import Payslip, PaymentStatus\n    \n    payslips = Payslip.objects.filter(payroll_run=payroll_run)\n    transfer_data = []\n    \n    for payslip in payslips:\n        try:\n            payment_status = payslip.payment_status\n            if payment_status.status == 'PENDING' and payment_status.payment_mode == 'BANK_TRANSFER':\n                transfer_data.append({\n                    'employee_name': payslip.employee.get_full_name(),\n                    'account_number': payment_status.bank_account_number,\n                    'ifsc_code': payment_status.ifsc_code,\n                    'amount': float(payslip.net_salary),\n                    'employee_id': payslip.employee.id,\n                })\n        except PaymentStatus.DoesNotExist:\n            continue\n    \n    return transfer_data
