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
        other_allowances = other_allowances * lop_factor
    
    # Calculate overtime pay
    overtime_pay = Decimal(0)
    if overtime_hours > 0 and salary_structure.salary_type != 'CONTRACT':
        hourly_rate = basic / (working_days * 8)  # Assuming 8 hours per day
        overtime_rate = salary_structure.overtime_rate
        overtime_pay = quant(hourly_rate * Decimal(overtime_hours) * overtime_rate)
    
    # Calculate bonuses for this period
    bonus_amount = Decimal(0)
    if payroll_run and salary_structure.bonus_eligible:
        bonuses = Bonus.objects.filter(
            employee=salary_structure.employee,
            applicable_month=payroll_run.month,
            applicable_year=payroll_run.year,
            is_processed=False
        )
        for bonus in bonuses:
            bonus_amount += quant(bonus.calculate_amount(basic))
    
    # Calculate reimbursements
    reimbursement_amount = Decimal(0)
    if payroll_run:
        approved_reimbursements = Reimbursement.objects.filter(
            employee=salary_structure.employee,
            status='APPROVED',
            paid_in_payroll__isnull=True
        )
        for reimbursement in approved_reimbursements:
            reimbursement_amount += quant(reimbursement.amount)
    
    # Calculate gross salary
    gross_salary = (
        basic + hra + medical_allowance + special_allowance + 
        conveyance + other_allowances + overtime_pay + bonus_amount + reimbursement_amount
    )
    
    # === STATUTORY DEDUCTIONS ===
    
    # Provident Fund (PF) - 12% of basic, max limit as per policy
    pf_percent = Decimal(salary_structure.pf_percent) / Decimal(100)
    pf_basic = min(basic, Decimal(policy.get('pf_salary_limit', 15000)))  # PF limit
    pf_deduction = quant(pf_basic * pf_percent)
    
    # Employee State Insurance (ESI) - 0.75% if salary <= ESI limit
    esi_deduction = Decimal(0)
    esi_limit = Decimal(policy.get('esi_salary_limit', 21000))
    if gross_salary <= esi_limit:
        esi_percent = Decimal(salary_structure.esi_percent) / Decimal(100)
        esi_deduction = quant(gross_salary * esi_percent)
    
    # Professional Tax (PT) - State-specific slabs
    professional_tax = calculate_professional_tax(gross_salary, policy)
    
    # Income Tax (TDS) - Based on annual projections
    income_tax = calculate_income_tax(basic, gross_salary, salary_structure, policy)
    
    # === OTHER DEDUCTIONS ===
    
    # Loan EMI deductions
    loan_deduction = Decimal(0)
    if payroll_run:
        active_loans = EmployeeLoan.objects.filter(
            employee=salary_structure.employee,
            status='ACTIVE',
            remaining_amount__gt=0
        )
        for loan in active_loans:
            emi_amount = min(loan.emi_amount, loan.remaining_amount)
            loan_deduction += quant(emi_amount)
    
    # Custom deduction components
    custom_deductions = Decimal(0)
    deduction_components = PayrollComponent.objects.filter(
        component_type='DEDUCTION',
        is_active=True
    )
    
    deduction_details = {}
    for component in deduction_components:
        if component.min_salary_threshold and gross_salary < component.min_salary_threshold:
            continue
        if component.max_salary_threshold and gross_salary > component.max_salary_threshold:
            continue
            
        if component.calculation_type == 'FIXED':
            deduction_amount = component.default_value
        elif component.calculation_type == 'PERCENTAGE':
            deduction_amount = (basic * component.default_value / 100)
        elif component.calculation_type == 'PERCENTAGE_GROSS':
            deduction_amount = (gross_salary * component.default_value / 100)
        else:
            deduction_amount = 0
            
        deduction_amount = quant(deduction_amount)
        custom_deductions += deduction_amount
        deduction_details[component.name.lower().replace(' ', '_')] = float(deduction_amount)
    
    # Total deductions
    total_deductions = (
        pf_deduction + esi_deduction + professional_tax + 
        income_tax + loan_deduction + custom_deductions
    )
    
    # Net salary
    net_salary = quant(gross_salary - total_deductions)
    
    # Detailed components breakdown
    components = {
        # Earnings
        'basic': float(basic),
        'hra': float(hra),
        'medical_allowance': float(medical_allowance),
        'special_allowance': float(special_allowance),
        'conveyance': float(conveyance),
        'other_allowances': float(other_allowances),
        'overtime_pay': float(overtime_pay),
        'bonus': float(bonus_amount),
        'reimbursements': float(reimbursement_amount),
        'gross_salary': float(gross_salary),
        
        # Deductions
        'pf_deduction': float(pf_deduction),
        'esi_deduction': float(esi_deduction),
        'professional_tax': float(professional_tax),
        'income_tax': float(income_tax),
        'loan_deduction': float(loan_deduction),
        'total_deductions': float(total_deductions),
        
        # Net
        'net_salary': float(net_salary),
        
        # Attendance details
        'working_days': working_days,
        'present_days': present_days,
        'lop_days': lop_days,
        'overtime_hours': overtime_hours,
    }
    
    # Add custom deduction details
    components.update(deduction_details)
    
    return {
        'gross_salary': gross_salary,
        'total_deductions': total_deductions,
        'net_salary': net_salary,
        'components': components,
        'attendance_summary': attendance_summary
    }


def calculate_professional_tax(gross_salary, policy=None):
    """
    Calculate Professional Tax based on salary slabs.
    This is a simplified version - implement state-specific PT slabs.
    """
    if policy is None:
        policy = {}
    
    # Default PT slabs (can be overridden in policy)
    pt_slabs = policy.get('pt_slabs', [
        {'min': 0, 'max': 10000, 'tax': 0},
        {'min': 10001, 'max': 15000, 'tax': 150},
        {'min': 15001, 'max': 25000, 'tax': 200},
        {'min': 25001, 'max': float('inf'), 'tax': 300},
    ])
    
    for slab in pt_slabs:
        if slab['min'] <= gross_salary <= slab['max']:
            return Decimal(slab['tax'])
    
    return Decimal(0)


def calculate_income_tax(basic_salary, gross_salary, salary_structure, policy=None):
    """
    Calculate monthly income tax based on annual projections.
    This is a simplified version - implement proper tax calculations with exemptions.
    """
    if policy is None:
        policy = {}
    
    # Annual gross projection
    annual_gross = gross_salary * 12
    
    # Tax slabs (FY 2024-25 - New Tax Regime)
    tax_slabs = policy.get('tax_slabs', [
        {'min': 0, 'max': 300000, 'rate': 0},
        {'min': 300001, 'max': 700000, 'rate': 5},
        {'min': 700001, 'max': 1000000, 'rate': 10},
        {'min': 1000001, 'max': 1200000, 'rate': 15},
        {'min': 1200001, 'max': 1500000, 'rate': 20},
        {'min': 1500001, 'max': float('inf'), 'rate': 30},
    ])
    
    annual_tax = Decimal(0)
    for slab in tax_slabs:
        if annual_gross > slab['min']:
            taxable_amount = min(annual_gross, slab['max']) - slab['min'] + 1
            if taxable_amount > 0:
                annual_tax += (taxable_amount * Decimal(slab['rate']) / 100)
    
    # Monthly tax deduction
    monthly_tax = annual_tax / 12
    return quant(monthly_tax)


def get_attendance_summary_for_employee(employee, year, month):
    """
    Get attendance summary for payroll calculation.
    Integrates with attendance module.
    """
    try:
        from apps.attendance.models import AttendanceRecord
        from datetime import date, timedelta

        # Get working days in month excluding weekends and holidays
        _, last_day = monthrange(year, month)
        working_days = 0
        for d in range(1, last_day + 1):
            day = date(year, month, d)
            # Skip weekends
            if day.weekday() >= 5:
                continue
            # Skip holidays (uses apps.holidays.models if available)
            try:
                if is_holiday(day):
                    continue
            except Exception:
                # If holidays app not available or any error, ignore
                pass
            # Count this day as a working day
            working_days += 1

        # Get attendance records for the month
        attendance_records = AttendanceRecord.objects.filter(
            employee__user=employee,
            clock_in__year=year,
            clock_in__month=month
        )
        
        present_days = attendance_records.filter(clock_out__isnull=False).count()
        total_overtime = attendance_records.aggregate(
            total_ot=Sum('overtime_hours')
        )['total_ot'] or 0
        
        # Calculate LOP days
        lop_days = max(0, working_days - present_days)
        
        return {
            'working_days_in_month': working_days,
            'present_days': present_days,
            'overtime_hours': float(total_overtime),
            'lop_days': lop_days
        }
        
    except ImportError:
        # Attendance module not available
        return {
            'working_days_in_month': 30,
            'present_days': 30,
            'overtime_hours': 0,
            'lop_days': 0
        }


def is_holiday(check_date, country: str | None = None) -> bool:
    """
    Returns True if `check_date` is a holiday. Handles recurring holidays.
    """
    try:
        from apps.holidays.models import Holiday
        # Exact-date non-recurring holiday
        if Holiday.objects.filter(date=check_date, is_recurring=False).exists():
            return True
        # Recurring holiday: match month/day
        if Holiday.objects.filter(is_recurring=True, date__month=check_date.month, date__day=check_date.day).exists():
            return True
        # Optionally scope by country
        if country:
            if Holiday.objects.filter(date=check_date, country=country).exists():
                return True
            if Holiday.objects.filter(is_recurring=True, date__month=check_date.month, date__day=check_date.day, country=country).exists():
                return True
    except Exception:
        return False

    return False


def generate_bank_transfer_file(payroll_run):
    """
    Generate bank transfer file for bulk salary payments.
    Returns CSV format data for bank upload.
    """
    from .models import Payslip, PaymentStatus
    
    payslips = Payslip.objects.filter(payroll_run=payroll_run)
    transfer_data = []
    
    for payslip in payslips:
        try:
            payment_status = payslip.payment_status
            if payment_status.status == 'PENDING' and payment_status.payment_mode == 'BANK_TRANSFER':
                transfer_data.append({
                    'employee_name': payslip.employee.get_full_name(),
                    'account_number': payment_status.bank_account_number,
                    'ifsc_code': payment_status.ifsc_code,
                    'amount': float(payslip.net_salary),
                    'employee_id': payslip.employee.id,
                })
        except PaymentStatus.DoesNotExist:
            continue
    
    return transfer_data