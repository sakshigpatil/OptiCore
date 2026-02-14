# from django.db import models
# from django.core.validators import MinValueValidator
# from apps.employees.models import Employee


# class PayrollRecord(models.Model):
#     """Payroll record model"""
    
#     STATUS_CHOICES = [
#         ('DRAFT', 'Draft'),
#         ('PROCESSED', 'Processed'),
#         ('PAID', 'Paid'),
#         ('CANCELLED', 'Cancelled'),
#     ]
    
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_records')
#     pay_period_start = models.DateField()
#     pay_period_end = models.DateField()
#     base_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
#     # Deductions
#     tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
#     gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
#     net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
#     pay_date = models.DateField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ['employee', 'pay_period_start', 'pay_period_end']
#         ordering = ['-pay_period_start']
    
#     def __str__(self):
#         return f"{self.employee.user.get_full_name()} - {self.pay_period_start} to {self.pay_period_end}"
    
#     def save(self, *args, **kwargs):
#         # Calculate gross salary
#         self.gross_salary = (
#             self.base_salary + 
#             self.overtime_pay + 
#             self.bonuses + 
#             self.allowances
#         )
        
#         # Calculate total deductions
#         self.total_deductions = (
#             self.tax_deduction + 
#             self.insurance_deduction + 
#             self.provident_fund + 
#             self.other_deductions
#         )
        
#         # Calculate net salary
#         self.net_salary = self.gross_salary - self.total_deductions
        
#         super().save(*args, **kwargs)


# class PayrollComponent(models.Model):
#     """Configurable payroll components"""
    
#     COMPONENT_TYPE_CHOICES = [
#         ('EARNING', 'Earning'),
#         ('DEDUCTION', 'Deduction'),
#     ]
    
#     name = models.CharField(max_length=100, unique=True)
#     component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)
#     is_percentage = models.BooleanField(default=False)
#     default_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     is_mandatory = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
    
#     def __str__(self):
#         return f"{self.name} ({self.component_type})"


from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL

def quant(x):
    return Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class SalaryStructure(models.Model):
    """
    Define comprehensive salary components for an employee.
    """
    SALARY_TYPE_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('HOURLY', 'Hourly'),
        ('CONTRACT', 'Contract'),
        ('DAILY', 'Daily'),
    ]
    
    employee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_structure')
    
    # Basic Salary Information
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, default='MONTHLY')
    basic = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Allowances
    hra_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20, validators=[MinValueValidator(0), MaxValueValidator(100)])
    hra_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    conveyance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Deductions
    pf_percent = models.DecimalField(max_digits=5, decimal_places=2, default=12, validators=[MinValueValidator(0), MaxValueValidator(100)])
    esi_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.75, validators=[MinValueValidator(0), MaxValueValidator(100)])
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Bonus & Incentives
    bonus_eligible = models.BooleanField(default=True)
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.5, validators=[MinValueValidator(1)])  # Multiplier for OT
    
    # CTC Components
    annual_ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Effective Date
    effective_from = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_hra_amount(self):
        """Calculate HRA - either percentage of basic or fixed amount"""
        if self.hra_fixed > 0:
            return self.hra_fixed
        return (self.basic * self.hra_percent / 100)
    
    def get_monthly_ctc(self):
        """Calculate monthly CTC from annual"""
        return self.annual_ctc / 12 if self.annual_ctc > 0 else 0

    def __str__(self):
        return f"SalaryStructure {self.employee} - Basic: {self.basic} ({self.salary_type})"

class PayrollRun(models.Model):
    """
    Represents a monthly payroll run (one per month).
    """
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()  # 1-12
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('year', 'month')
        ordering = ('-year', '-month')

    def __str__(self):
        return f"Payroll {self.year}-{self.month:02d}"

class Payslip(models.Model):
    """
    Payslip per employee per payroll run (stores snapshot of computed values).
    """
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payslips')
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    components = models.JSONField(default=dict)  # {"basic":..., "hra":..., "pf":..., "tax":...}
    generated_at = models.DateTimeField(auto_now_add=True)
    # optional: path to generated PDF if you save it
    payslip_pdf = models.FileField(upload_to='payslips/', null=True, blank=True)

    class Meta:
        unique_together = ('payroll_run', 'employee')

    def __str__(self):
        return f"Payslip: {self.employee} {self.payroll_run.year}-{self.payroll_run.month:02d}"


class EmployeeLoan(models.Model):
    """
    Employee loan management for salary deductions.
    """
    LOAN_TYPE_CHOICES = [
        ('PERSONAL', 'Personal Loan'),
        ('ADVANCE', 'Salary Advance'),
        ('EMERGENCY', 'Emergency Loan'),
        ('EDUCATION', 'Education Loan'),
        ('MEDICAL', 'Medical Loan'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    loan_tenure = models.IntegerField(validators=[MinValueValidator(1)])  # in months
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.remaining_amount:
            self.remaining_amount = self.loan_amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee} - {self.loan_type} - {self.loan_amount}"


class Bonus(models.Model):
    """
    Bonus management for employees.
    """
    BONUS_TYPE_CHOICES = [
        ('FESTIVAL', 'Festival Bonus'),
        ('PERFORMANCE', 'Performance Bonus'),
        ('REFERRAL', 'Referral Bonus'),
        ('SALES', 'Sales Incentive'),
        ('ANNUAL', 'Annual Bonus'),
        ('PROJECT', 'Project Bonus'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses')
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    percentage_of_basic = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    applicable_month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    applicable_year = models.PositiveSmallIntegerField()
    
    is_processed = models.BooleanField(default=False)
    processed_in_payroll = models.ForeignKey(PayrollRun, on_delete=models.SET_NULL, null=True, blank=True)
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bonuses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_amount(self, basic_salary):
        """Calculate bonus amount based on basic salary if percentage is set"""
        if self.percentage_of_basic:
            return (basic_salary * self.percentage_of_basic / 100)
        return self.amount
    
    def __str__(self):
        return f"{self.employee} - {self.bonus_type} - {self.amount}"


class Reimbursement(models.Model):
    """
    Employee reimbursement claims.
    """
    REIMBURSEMENT_TYPE_CHOICES = [
        ('TRAVEL', 'Travel Reimbursement'),
        ('FOOD', 'Food Reimbursement'),
        ('MEDICAL', 'Medical Reimbursement'),
        ('MOBILE', 'Mobile/Internet'),
        ('FUEL', 'Fuel Reimbursement'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reimbursements')
    reimbursement_type = models.CharField(max_length=20, choices=REIMBURSEMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    
    claim_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reimbursements')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Link to payroll when paid
    paid_in_payroll = models.ForeignKey(PayrollRun, on_delete=models.SET_NULL, null=True, blank=True)
    
    # File attachment for bills/receipts
    receipt_file = models.FileField(upload_to='reimbursements/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee} - {self.reimbursement_type} - {self.amount}"


class PayrollComponent(models.Model):
    """
    Configurable payroll components for custom earnings/deductions.
    """
    COMPONENT_TYPE_CHOICES = [
        ('EARNING', 'Earning'),
        ('DEDUCTION', 'Deduction'),
    ]
    
    CALCULATION_TYPE_CHOICES = [
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE', 'Percentage of Basic'),
        ('PERCENTAGE_GROSS', 'Percentage of Gross'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPE_CHOICES, default='FIXED')
    default_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_mandatory = models.BooleanField(default=False)
    is_statutory = models.BooleanField(default=False)  # PF, ESI, PT etc.
    is_active = models.BooleanField(default=True)
    
    # Salary thresholds for applicability
    min_salary_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_salary_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.component_type})"


class PaymentStatus(models.Model):
    """
    Track payment status for each payslip.
    """
    PAYMENT_MODE_CHOICES = [
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('UPI', 'UPI'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('ON_HOLD', 'On Hold'),
        ('FAILED', 'Failed'),
    ]
    
    payslip = models.OneToOneField(Payslip, on_delete=models.CASCADE, related_name='payment_status')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='BANK_TRANSFER')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    payment_date = models.DateField(null=True, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    
    # Bank details for transfer
    bank_account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payslip.employee} - {self.status} - {self.payment_mode}"
