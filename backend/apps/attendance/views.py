from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from datetime import datetime, date, timedelta
from decimal import Decimal
from .models import AttendanceRecord, AttendanceSettings
from .serializers import (
    AttendanceRecordSerializer, ClockInSerializer, ClockOutSerializer,
    AttendanceHistorySerializer, AttendanceStatsSerializer, AttendanceSettingsSerializer
)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for attendance records with clock-in/clock-out functionality"""
    
    queryset = AttendanceRecord.objects.select_related('employee__user', 'employee__department').all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['date', 'employee', 'status', 'is_overtime']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'clock_in_time', 'clock_out_time', 'total_hours']
    ordering = ['-date', '-clock_in_time']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # If user is an employee, only show their own records
        if hasattr(user, 'employee') and user.role == 'EMPLOYEE':
            queryset = queryset.filter(employee=user.employee)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def clock_in(self, request):
        """Clock in endpoint"""
        serializer = ClockInSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                attendance = serializer.save()
                response_serializer = AttendanceRecordSerializer(attendance)
                return Response({
                    'success': True,
                    'message': 'Successfully clocked in',
                    'data': response_serializer.data
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def clock_out(self, request):
        """Clock out endpoint"""
        serializer = ClockOutSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                attendance = serializer.save()
                response_serializer = AttendanceRecordSerializer(attendance)
                return Response({
                    'success': True,
                    'message': 'Successfully clocked out',
                    'data': response_serializer.data
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def current_status(self, request):
        """Get current attendance status for employee"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response({
                'success': False,
                'message': 'Employee ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            today = date.today()
            attendance = AttendanceRecord.objects.get(
                employee_id=employee_id,
                date=today
            )
            serializer = AttendanceRecordSerializer(attendance)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except AttendanceRecord.DoesNotExist:
            return Response({
                'success': True,
                'data': {
                    'is_clocked_in': False,
                    'message': 'No attendance record for today'
                }
            })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get attendance history with filtering"""
        employee_id = request.query_params.get('employee_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AttendanceHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AttendanceHistorySerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get attendance statistics"""
        employee_id = request.query_params.get('employee_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start_date = date(today.year, today.month, 1)
            if today.month == 12:
                end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        queryset = self.get_queryset().filter(date__range=[start_date, end_date])
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Calculate statistics
        stats = queryset.aggregate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status__in=['PRESENT', 'LATE', 'OVERTIME'])),
            absent_days=Count('id', filter=Q(status='ABSENT')),
            late_days=Count('id', filter=Q(status='LATE')),
            total_hours=Sum('total_hours') or Decimal('0'),
            overtime_hours=Sum('overtime_hours') or Decimal('0'),
        )
        
        # Calculate derived statistics
        stats['average_hours'] = (
            stats['total_hours'] / stats['total_days'] 
            if stats['total_days'] > 0 else Decimal('0')
        )
        stats['attendance_percentage'] = (
            (stats['present_days'] / stats['total_days'] * 100) 
            if stats['total_days'] > 0 else Decimal('0')
        )
        
        serializer = AttendanceStatsSerializer(stats)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def today_summary(self, request):
        """Get today's attendance summary"""
        today = date.today()
        
        # Overall statistics
        total_employees = AttendanceRecord.objects.filter(date=today).count()
        present = AttendanceRecord.objects.filter(
            date=today, 
            status__in=['PRESENT', 'LATE', 'OVERTIME']
        ).count()
        clocked_in = AttendanceRecord.objects.filter(
            date=today,
            clock_in_time__isnull=False,
            clock_out_time__isnull=True
        ).count()
        
        # Recent clock-ins (last 10)
        recent_clockins = AttendanceRecord.objects.filter(
            date=today,
            clock_in_time__isnull=False
        ).select_related('employee__user').order_by('-clock_in_time')[:10]
        
        clockin_serializer = AttendanceHistorySerializer(recent_clockins, many=True)
        
        return Response({
            'success': True,
            'data': {
                'date': today,
                'total_employees': total_employees,
                'present_count': present,
                'currently_clocked_in': clocked_in,
                'absent_count': total_employees - present,
                'recent_clock_ins': clockin_serializer.data
            }
        })


class AttendanceSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for attendance settings"""
    
    queryset = AttendanceSettings.objects.all()
    serializer_class = AttendanceSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only HR admin can modify settings"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
            # Add custom permission check for HR admin
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current attendance settings"""
        settings = AttendanceSettings.get_settings()
        serializer = AttendanceSettingsSerializer(settings)
        return Response({
            'success': True,
            'data': serializer.data
        })


# Backward compatibility
class AttendanceViewSet(AttendanceRecordViewSet):
    """Backward compatibility alias"""
    pass