from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import LeaveType, LeaveRequest, ResignationRequest
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer, ResignationRequestSerializer
from apps.employees.models import Employee
from django.db.models import Sum
from django.utils import timezone

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

    def get_queryset(self):
        user = self.request.user
        
        # HR Admins, Staff, and Superusers can see all leave requests
        if (user.is_staff or user.is_superuser or user.role == 'ADMIN_HR'):
            return LeaveRequest.objects.all()
        
        # Managers can only see leave requests from their direct subordinates
        if user.role == 'MANAGER':
            try:
                manager_employee = Employee.objects.get(user=user)
                # Get all subordinates under this manager
                subordinate_employees = manager_employee.subordinates.all()
                # Return leave requests only from subordinates
                return LeaveRequest.objects.filter(employee__in=subordinate_employees)
            except Employee.DoesNotExist:
                return LeaveRequest.objects.none()
        
        # Regular employees can only see their own leave requests
        try:
            employee = Employee.objects.get(user=user)
            return LeaveRequest.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            return LeaveRequest.objects.none()

    def perform_create(self, serializer):
        # Automatically set the employee to current user
        try:
            employee = Employee.objects.get(user=self.request.user)
            serializer.save(employee=employee)
        except Employee.DoesNotExist:
            raise ValidationError("Employee profile not found for current user")

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get leave balance for current user"""
        try:
            employee = Employee.objects.get(user=request.user)
            
            # Calculate total used days this year
            used_days = LeaveRequest.objects.filter(
                employee=employee,
                status='APPROVED',
                start_date__year=2025
            ).aggregate(total=Sum('days_requested'))['total'] or 0
            
            # Get total allowed days (assuming 25 for now)
            total_days = 25
            remaining_days = total_days - used_days
            
            return Response({
                'total': total_days,
                'used': used_days,
                'remaining': remaining_days
            })
        except Employee.DoesNotExist:
            return Response({
                'total': 25,
                'used': 0,
                'remaining': 25
            })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request"""
        try:
            leave_request = self.get_object()
            
            # Check if user has permission to approve (HR, Manager, Staff, or Superuser)
            if not (request.user.is_staff or request.user.is_superuser or 
                    request.user.role == 'ADMIN_HR' or request.user.role == 'MANAGER'):
                return Response(
                    {'error': 'You do not have permission to approve leave requests'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # If user is a manager, ensure they can only approve requests from their subordinates
            if request.user.role == 'MANAGER':
                try:
                    manager_employee = Employee.objects.get(user=request.user)
                    if leave_request.employee.manager != manager_employee:
                        return Response(
                            {'error': 'You can only approve leave requests from your direct team members'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Employee.DoesNotExist:
                    return Response(
                        {'error': 'Manager employee profile not found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check if already processed
            if leave_request.status != 'PENDING':
                return Response(
                    {'error': 'Leave request has already been processed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get approver employee
            try:
                approver = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Approver employee profile not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Approve the leave request
            leave_request.status = 'APPROVED'
            leave_request.approved_by = approver
            leave_request.processed_on = timezone.now()
            leave_request.save()
            
            serializer = self.get_serializer(leave_request)
            return Response({
                'message': 'Leave request approved successfully',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave request"""
        try:
            leave_request = self.get_object()
            
            # Check if user has permission to reject (HR, Manager, Staff, or Superuser)
            if not (request.user.is_staff or request.user.is_superuser or 
                    request.user.role == 'ADMIN_HR' or request.user.role == 'MANAGER'):
                return Response(
                    {'error': 'You do not have permission to reject leave requests'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # If user is a manager, ensure they can only reject requests from their subordinates
            if request.user.role == 'MANAGER':
                try:
                    manager_employee = Employee.objects.get(user=request.user)
                    if leave_request.employee.manager != manager_employee:
                        return Response(
                            {'error': 'You can only reject leave requests from your direct team members'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Employee.DoesNotExist:
                    return Response(
                        {'error': 'Manager employee profile not found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check if already processed
            if leave_request.status != 'PENDING':
                return Response(
                    {'error': 'Leave request has already been processed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get rejection reason from request data
            rejection_reason = request.data.get('rejection_reason', 'No reason provided')
            
            # Get approver employee
            try:
                approver = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Approver employee profile not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reject the leave request
            leave_request.status = 'REJECTED'
            leave_request.approved_by = approver
            leave_request.rejection_reason = rejection_reason
            leave_request.processed_on = timezone.now()
            leave_request.save()
            
            serializer = self.get_serializer(leave_request)
            return Response({
                'message': 'Leave request rejected successfully',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResignationRequestViewSet(viewsets.ModelViewSet):
    queryset = ResignationRequest.objects.all()
    serializer_class = ResignationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['resignation_date', 'last_working_day', 'created_at']
    ordering = ['-created_at']