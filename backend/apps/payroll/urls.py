# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()
# router.register('payroll', views.PayrollRecordViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalaryStructureViewSet, PayrollRunViewSet, PayslipViewSet,
    EmployeeLoanViewSet, BonusViewSet, ReimbursementViewSet
)

router = DefaultRouter()
router.register(r'salary-structures', SalaryStructureViewSet, basename='salarystructure')
router.register(r'payroll-runs', PayrollRunViewSet, basename='payrollrun')
router.register(r'payslips', PayslipViewSet, basename='payslip')
router.register(r'loans', EmployeeLoanViewSet, basename='employeeloan')
router.register(r'bonuses', BonusViewSet, basename='bonus')
router.register(r'reimbursements', ReimbursementViewSet, basename='reimbursement')

urlpatterns = [
    path('', include(router.urls)),
]
