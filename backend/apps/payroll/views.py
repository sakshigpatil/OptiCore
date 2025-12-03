from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import PayrollRecord
from .serializers import PayrollRecordSerializer

class PayrollRecordViewSet(viewsets.ModelViewSet):
    queryset = PayrollRecord.objects.all()
    serializer_class = PayrollRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['month', 'year', 'employee']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['month', 'year', 'total_salary']
    ordering = ['-year', '-month']