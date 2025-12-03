from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import LeaveType, LeaveRequest, ResignationRequest
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer, ResignationRequestSerializer

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'leave_type']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

class ResignationRequestViewSet(viewsets.ModelViewSet):
    queryset = ResignationRequest.objects.all()
    serializer_class = ResignationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['resignation_date', 'last_working_day', 'created_at']
    ordering = ['-created_at']