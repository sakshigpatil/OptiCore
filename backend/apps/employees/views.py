from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Employee, Department, EmployeeDocument
from .serializers import (
    EmployeeSerializer, 
    EmployeeCreateSerializer,
    EmployeeProfileSerializer,
    DepartmentSerializer,
    EmployeeUpdateSerializer,
    EmployeeDocumentSerializer,
    EmployeeDocumentCreateSerializer
)
from core.permissions import IsHROrAdmin, IsManagerOrAbove, IsOwnerOrHR


class DepartmentViewSet(viewsets.ModelViewSet):
    """Department management viewset"""
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """HR/Admin can create/update/delete departments"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsHROrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class EmployeeViewSet(viewsets.ModelViewSet):
    """Employee management viewset"""
    queryset = Employee.objects.select_related('user', 'department', 'manager').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'status', 'position']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'position']
    ordering_fields = ['employee_id', 'user__first_name', 'hire_date']
    ordering = ['employee_id']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'destroy']:
            permission_classes = [IsHROrAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsHROrAdmin]
        elif self.action in ['list']:
            # HR and Managers can view all employees
            permission_classes = [IsManagerOrAbove]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action == 'update_profile':
            return EmployeeProfileSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's employee profile"""
        try:
            employee = request.user.employee
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's employee profile"""
        try:
            employee = request.user.employee
            serializer = self.get_serializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[IsHROrAdmin])
    def terminate(self, request, pk=None):
        """Terminate an employee"""
        employee = self.get_object()
        termination_date = request.data.get('termination_date')
        reason = request.data.get('reason', '')
        
        if not termination_date:
            return Response({'error': 'Termination date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        employee.status = 'TERMINATED'
        employee.termination_date = termination_date
        employee.save()
        
        # Create notification
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=employee.user,
            title='Employment Terminated',
            message=f'Your employment has been terminated. Reason: {reason}',
            notification_type='WARNING'
        )
        
        return Response({'message': 'Employee terminated successfully'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsManagerOrAbove])
    def subordinates(self, request):
        """Get employees under current manager"""
        if not hasattr(request.user, 'employee'):
            return Response({'error': 'User is not an employee'}, status=status.HTTP_400_BAD_REQUEST)
        
        subordinates = Employee.objects.filter(
            manager=request.user.employee,
            status='ACTIVE'
        ).select_related('user', 'department')
        
        serializer = self.get_serializer(subordinates, many=True)
        return Response(serializer.data)


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """Employee document management viewset"""
    queryset = EmployeeDocument.objects.select_related('employee', 'employee__user', 'uploaded_by').all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'document_type']
    search_fields = ['title', 'description', 'employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['created_at', 'title', 'document_type']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EmployeeDocumentCreateSerializer
        return EmployeeDocumentSerializer

    def get_queryset(self):
        user = self.request.user
        base_queryset = super().get_queryset()

        if user.role in ['ADMIN_HR', 'MANAGER']:
            return base_queryset

        if hasattr(user, 'employee'):
            return base_queryset.filter(employee=user.employee)

        return base_queryset.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsHROrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)