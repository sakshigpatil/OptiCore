# from rest_framework import serializers
# from .models import PayrollRecord

# class PayrollRecordSerializer(serializers.ModelSerializer):
#     employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
#     employee_id = serializers.CharField(source='employee.employee_id', read_only=True)

#     class Meta:
#         model = PayrollRecord
#         fields = '__all__'
#         read_only_fields = ('created_at', 'updated_at')

from rest_framework import serializers
from .models import (
    SalaryStructure, PayrollRun, Payslip, EmployeeLoan, 
    Bonus, Reimbursement, PayrollComponent, PaymentStatus
)
from django.contrib.auth import get_user_model

User = get_user_model()

class SalaryStructureSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    monthly_ctc = serializers.SerializerMethodField()
    
    class Meta:
        model = SalaryStructure
        fields = [
            'id', 'employee', 'employee_name', 'salary_type', 'basic', 
            'hra_percent', 'hra_fixed', 'conveyance', 'medical_allowance',
            'special_allowance', 'other_allowances', 'pf_percent', 'esi_percent',
            'professional_tax', 'bonus_eligible', 'overtime_rate', 'annual_ctc',
            'monthly_ctc', 'effective_from', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_monthly_ctc(self, obj):
        return obj.get_monthly_ctc()

class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    payroll_period = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'payroll_run', 'employee', 'employee_name', 'gross_salary', 
            'total_deductions', 'net_salary', 'components', 'generated_at', 
            'payslip_pdf', 'payroll_period', 'payment_status'
        ]
    
    def get_payroll_period(self, obj):
        return f"{obj.payroll_run.year}-{obj.payroll_run.month:02d}"
    
    def get_payment_status(self, obj):
        try:
            return {
                'status': obj.payment_status.status,
                'payment_mode': obj.payment_status.payment_mode,
                'payment_date': obj.payment_status.payment_date
            }
        except PaymentStatus.DoesNotExist:
            return None

class PayrollRunSerializer(serializers.ModelSerializer):
    payslip_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollRun
        fields = [
            'id', 'year', 'month', 'created_by', 'created_at', 'processed',
            'payslip_count', 'total_amount'
        ]
        read_only_fields = ['created_by', 'created_at', 'processed']
    
    def get_payslip_count(self, obj):
        return obj.payslips.count()
    
    def get_total_amount(self, obj):
        from django.db.models import Sum
        return obj.payslips.aggregate(total=Sum('net_salary'))['total'] or 0

class EmployeeLoanSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeLoan
        fields = [
            'id', 'employee', 'employee_name', 'loan_type', 'loan_amount',
            'emi_amount', 'loan_tenure', 'remaining_amount', 'status',
            'approved_by', 'approved_by_name', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['approved_by', 'created_at', 'updated_at']

class BonusSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    calculated_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Bonus
        fields = [
            'id', 'employee', 'employee_name', 'bonus_type', 'amount',
            'percentage_of_basic', 'applicable_month', 'applicable_year',
            'is_processed', 'processed_in_payroll', 'approved_by',
            'approved_by_name', 'calculated_amount', 'created_at'
        ]
        read_only_fields = ['approved_by', 'created_at', 'is_processed', 'processed_in_payroll']
    
    def get_calculated_amount(self, obj):
        if obj.percentage_of_basic and obj.employee.salary_structure:
            basic_salary = obj.employee.salary_structure.basic
            return obj.calculate_amount(basic_salary)
        return obj.amount

class ReimbursementSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Reimbursement
        fields = [
            'id', 'employee', 'employee_name', 'reimbursement_type', 'amount',
            'description', 'claim_date', 'status', 'approved_by', 'approved_by_name',
            'approved_date', 'paid_in_payroll', 'receipt_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['employee', 'approved_by', 'created_at', 'updated_at']

class PayrollComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollComponent
        fields = [
            'id', 'name', 'component_type', 'calculation_type', 'default_value',
            'is_mandatory', 'is_statutory', 'is_active', 'min_salary_threshold',
            'max_salary_threshold', 'created_at'
        ]
        read_only_fields = ['created_at']

class PaymentStatusSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='payslip.employee.get_full_name', read_only=True)
    net_salary = serializers.DecimalField(source='payslip.net_salary', max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = PaymentStatus
        fields = [
            'id', 'payslip', 'employee_name', 'net_salary', 'payment_mode', 'status',
            'payment_date', 'transaction_reference', 'bank_account_number',
            'ifsc_code', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
