from django.db import models
from django.core.validators import MinValueValidator
from apps.employees.models import Employee


class PayrollRecord(models.Model):
    """Payroll record model"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_records')
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    pay_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'pay_period_start', 'pay_period_end']
        ordering = ['-pay_period_start']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.pay_period_start} to {self.pay_period_end}"
    
    def save(self, *args, **kwargs):
        # Calculate gross salary
        self.gross_salary = (
            self.base_salary + 
            self.overtime_pay + 
            self.bonuses + 
            self.allowances
        )
        
        # Calculate total deductions
        self.total_deductions = (
            self.tax_deduction + 
            self.insurance_deduction + 
            self.provident_fund + 
            self.other_deductions
        )
        
        # Calculate net salary
        self.net_salary = self.gross_salary - self.total_deductions
        
        super().save(*args, **kwargs)


class PayrollComponent(models.Model):
    """Configurable payroll components"""
    
    COMPONENT_TYPE_CHOICES = [
        ('EARNING', 'Earning'),
        ('DEDUCTION', 'Deduction'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)
    is_percentage = models.BooleanField(default=False)
    default_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.component_type})"