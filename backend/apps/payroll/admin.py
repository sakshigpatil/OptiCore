from django.contrib import admin
from .models import (
    SalaryStructure, PayrollRun, Payslip, EmployeeLoan, 
    Bonus, Reimbursement, PayrollComponent, PaymentStatus
)

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('employee', 'salary_type', 'basic', 'annual_ctc', 'is_active', 'effective_from')
    list_filter = ('salary_type', 'is_active', 'bonus_eligible')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'created_by', 'processed', 'created_at')
    list_filter = ('year', 'month', 'processed')
    readonly_fields = ('created_at',)

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll_run', 'gross_salary', 'net_salary', 'generated_at')
    list_filter = ('payroll_run__year', 'payroll_run__month')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('generated_at',)

@admin.register(EmployeeLoan)
class EmployeeLoanAdmin(admin.ModelAdmin):
    list_display = ('employee', 'loan_type', 'loan_amount', 'emi_amount', 'remaining_amount', 'status')
    list_filter = ('loan_type', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ('employee', 'bonus_type', 'amount', 'applicable_month', 'applicable_year', 'is_processed')
    list_filter = ('bonus_type', 'is_processed', 'applicable_year')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at',)

@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reimbursement_type', 'amount', 'claim_date', 'status', 'approved_by')
    list_filter = ('reimbursement_type', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PayrollComponent)
class PayrollComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'component_type', 'calculation_type', 'default_value', 'is_active')
    list_filter = ('component_type', 'calculation_type', 'is_active', 'is_statutory')

@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('payslip', 'payment_mode', 'status', 'payment_date', 'transaction_reference')
    list_filter = ('payment_mode', 'status', 'payment_date')
    search_fields = ('payslip__employee__first_name', 'payslip__employee__last_name', 'transaction_reference')
    readonly_fields = ('created_at', 'updated_at')
