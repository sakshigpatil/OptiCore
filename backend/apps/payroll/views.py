# from rest_framework import viewsets, permissions, status
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import SearchFilter, OrderingFilter
# from .models import PayrollRecord
# from .serializers import PayrollRecordSerializer

# class PayrollRecordViewSet(viewsets.ModelViewSet):
#     queryset = PayrollRecord.objects.all()
#     serializer_class = PayrollRecordSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_fields = ['month', 'year', 'employee']
#     search_fields = ['employee__user__first_name', 'employee__user__last_name']
#     ordering_fields = ['month', 'year', 'total_salary']
#     ordering = ['-year', '-month']

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from .models import (
    SalaryStructure, PayrollRun, Payslip, EmployeeLoan, 
    Bonus, Reimbursement, PayrollComponent, PaymentStatus
)
from .serializers import (
    SalaryStructureSerializer, PayrollRunSerializer, PayslipSerializer,
    EmployeeLoanSerializer, BonusSerializer, ReimbursementSerializer
)
from .utils import (
    calculate_payslip_for_employee, get_attendance_summary_for_employee,
    generate_bank_transfer_file
)
from django.db import transaction
from django.contrib.auth import get_user_model
import csv
from io import StringIO
User = get_user_model()

# Optional: For PDF generation
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
import tempfile, os

try:
    # WeasyPrint optional
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsAuthenticated]  # tighten later

    def get_queryset(self):
        user = self.request.user
        qs = SalaryStructure.objects.all()
        if not user.is_staff and not user.is_superuser:
            qs = qs.filter(employee=user)
        return qs

class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [IsAuthenticated]  # require admin for creating runs

    def get_permissions(self):
        # Allow ADMIN_HR users to access payroll runs
        if self.action in ('create', 'run', 'list', 'destroy'):
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN_HR', 'MANAGER'] or user.is_superuser:
            return PayrollRun.objects.all()
        return PayrollRun.objects.none()

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """
        Trigger payroll calculations for this PayrollRun.
        """
        payroll_run = self.get_object()
        if payroll_run.processed:
            return Response({'detail':'Payroll already processed for this month.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally accept policy overrides in request.data
        policy = request.data.get('policy', {})

        employees = User.objects.filter(is_active=True)
        with transaction.atomic():
            for emp in employees:
                try:
                    salary_struct = emp.salary_structure
                except SalaryStructure.DoesNotExist:
                    # skip employees without salary structure
                    continue
                calc = calculate_payslip_for_employee(salary_struct, attendance_summary=None, policy=policy)

                payslip = Payslip.objects.create(
                    payroll_run=payroll_run,
                    employee=emp,
                    gross_salary=calc['gross_salary'],
                    total_deductions=calc['total_deductions'],
                    net_salary=calc['net_salary'],
                    components=calc['components'],
                )

                # generate PDF optionally
                if WEASYPRINT_AVAILABLE:
                    html = render_to_string('payroll/payslip_template.html', {
                        'employee': emp,
                        'payroll_run': payroll_run,
                        'payslip': payslip,
                    })
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmpf:
                        HTML(string=html).write_pdf(tmpf.name)
                        tmpf.seek(0)
                        payslip.payslip_pdf.save(f"payslip_{emp.pk}_{payroll_run.year}_{payroll_run.month}.pdf", ContentFile(open(tmpf.name, 'rb').read()))
                        os.unlink(tmpf.name)
                # else: skip PDF generation (or implement xhtml2pdf)

            payroll_run.processed = True
            payroll_run.save()

        serializer = PayslipSerializer(payroll_run.payslips.all(), many=True)
        return Response({'detail':'Payroll processed', 'payslips': serializer.data}, status=status.HTTP_200_OK)

class PayslipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payslip.objects.all()
        if not user.is_staff and not user.is_superuser:
            qs = qs.filter(employee=user)
        # optional filters ?year=&month=&employee_id=
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        emp_id = self.request.query_params.get('employee_id')
        if year and month:
            qs = qs.filter(payroll_run__year=int(year), payroll_run__month=int(month))
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        return qs.order_by('-payroll_run__year', '-payroll_run__month')
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark a payslip as paid.
        """
        payslip = self.get_object()
        payment_data = request.data
        
        try:
            payment_status = payslip.payment_status
            payment_status.status = 'PAID'
            payment_status.payment_date = timezone.now().date()
            payment_status.payment_mode = payment_data.get('payment_mode', payment_status.payment_mode)
            payment_status.transaction_reference = payment_data.get('transaction_reference', '')
            payment_status.save()
            
            return Response({'detail': 'Payslip marked as paid'}, status=status.HTTP_200_OK)
        except PaymentStatus.DoesNotExist:
            return Response({'error': 'Payment status not found'}, status=status.HTTP_404_NOT_FOUND)


class EmployeeLoanViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLoan.objects.all()
    serializer_class = EmployeeLoanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return EmployeeLoan.objects.all().order_by('-created_at')
        return EmployeeLoan.objects.filter(employee=user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a loan request.
        """
        loan = self.get_object()
        if loan.status != 'PENDING':
            return Response({'error': 'Loan is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        
        loan.status = 'APPROVED'
        loan.approved_by = request.user
        loan.save()
        
        return Response({'detail': 'Loan approved successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate an approved loan to start EMI deductions.
        """
        loan = self.get_object()
        if loan.status != 'APPROVED':
            return Response({'error': 'Loan must be approved first'}, status=status.HTTP_400_BAD_REQUEST)
        
        loan.status = 'ACTIVE'
        loan.start_date = timezone.now().date()
        # Calculate end date
        from dateutil.relativedelta import relativedelta
        loan.end_date = loan.start_date + relativedelta(months=loan.loan_tenure)
        loan.save()
        
        return Response({'detail': 'Loan activated successfully'}, status=status.HTTP_200_OK)


class BonusViewSet(viewsets.ModelViewSet):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Bonus.objects.all().order_by('-created_at')
        return Bonus.objects.filter(employee=user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create bonuses for multiple employees.
        """
        bonus_data = request.data
        employee_ids = bonus_data.get('employee_ids', [])
        
        bonuses_created = []
        for emp_id in employee_ids:
            try:
                employee = User.objects.get(id=emp_id)
                bonus = Bonus.objects.create(
                    employee=employee,
                    bonus_type=bonus_data['bonus_type'],
                    amount=bonus_data.get('amount', 0),
                    percentage_of_basic=bonus_data.get('percentage_of_basic'),
                    applicable_month=bonus_data['applicable_month'],
                    applicable_year=bonus_data['applicable_year'],
                    approved_by=request.user
                )
                bonuses_created.append(bonus.id)
            except User.DoesNotExist:
                continue
        
        return Response({
            'detail': f'{len(bonuses_created)} bonuses created successfully',
            'bonus_ids': bonuses_created
        }, status=status.HTTP_201_CREATED)


class ReimbursementViewSet(viewsets.ModelViewSet):
    queryset = Reimbursement.objects.all()
    serializer_class = ReimbursementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Reimbursement.objects.all().order_by('-created_at')
        return Reimbursement.objects.filter(employee=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a reimbursement request.
        """
        reimbursement = self.get_object()
        if reimbursement.status != 'PENDING':
            return Response({'error': 'Reimbursement is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        
        reimbursement.status = 'APPROVED'
        reimbursement.approved_by = request.user
        reimbursement.approved_date = timezone.now()
        reimbursement.save()
        
        return Response({'detail': 'Reimbursement approved successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a reimbursement request.
        """
        reimbursement = self.get_object()
        if reimbursement.status != 'PENDING':
            return Response({'error': 'Reimbursement is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        
        reimbursement.status = 'REJECTED'
        reimbursement.approved_by = request.user
        reimbursement.approved_date = timezone.now()
        reimbursement.save()
        
        return Response({'detail': 'Reimbursement rejected'}, status=status.HTTP_200_OK)
