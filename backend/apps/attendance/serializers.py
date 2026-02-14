from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, date
from .models import AttendanceRecord, AttendanceSettings


class EmployeeBasicSerializer(serializers.Serializer):
    """Basic employee info for attendance records"""
    employee_id = serializers.CharField()
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email
        }

class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord model"""
    
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_id_field = serializers.CharField(source='employee.employee_id', read_only=True)
    employee = EmployeeBasicSerializer(read_only=True)
    is_clocked_in = serializers.BooleanField(read_only=True)
    working_duration = serializers.FloatField(read_only=True)
    clock_in_display = serializers.SerializerMethodField()
    clock_out_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_id_field', 'date',
            'clock_in_time', 'clock_out_time', 'total_hours', 'break_duration',
            'status', 'notes', 'location', 'ip_address', 'is_overtime',
            'overtime_hours', 'is_clocked_in', 'working_duration',
            'clock_in_display', 'clock_out_display', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'total_hours', 'is_overtime', 'overtime_hours', 'is_clocked_in',
            'working_duration', 'created_at', 'updated_at'
        )
    
    def get_clock_in_display(self, obj):
        """Format clock in time for display"""
        if obj.clock_in_time:
            return obj.clock_in_time.strftime('%H:%M:%S')
        return None
    
    def get_clock_out_display(self, obj):
        """Format clock out time for display"""
        if obj.clock_out_time:
            return obj.clock_out_time.strftime('%H:%M:%S')
        return None


class ClockInSerializer(serializers.Serializer):
    """Serializer for clock-in action"""
    
    employee = serializers.IntegerField()
    timestamp = serializers.DateTimeField(required=False)
    location = serializers.CharField(max_length=255, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    
    def validate_employee(self, value):
        """Validate employee exists"""
        from apps.employees.models import Employee
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found")
    
    def validate_timestamp(self, value):
        """Validate timestamp is not in future"""
        if value and value > timezone.now():
            raise serializers.ValidationError("Clock-in time cannot be in the future")
        return value
    
    def create(self, validated_data):
        """Create or get today's attendance record and clock in"""
        employee = validated_data['employee']
        today = validated_data.get('timestamp', timezone.now()).date()
        
        # Get or create today's attendance record
        attendance, created = AttendanceRecord.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'status': 'ABSENT'
            }
        )
        
        # Clock in
        attendance.clock_in(
            timestamp=validated_data.get('timestamp'),
            location=validated_data.get('location'),
            ip_address=self.context.get('request').META.get('REMOTE_ADDR')
        )
        
        if validated_data.get('notes'):
            attendance.notes = validated_data['notes']
            attendance.save()
        
        return attendance


class ClockOutSerializer(serializers.Serializer):
    """Serializer for clock-out action"""
    
    employee = serializers.IntegerField()
    timestamp = serializers.DateTimeField(required=False)
    location = serializers.CharField(max_length=255, required=False)
    notes = serializers.CharField(max_length=500, required=False)
    break_duration = serializers.DecimalField(max_digits=4, decimal_places=2, required=False, min_value=0)
    
    def validate_employee(self, value):
        """Validate employee exists and is clocked in"""
        from apps.employees.models import Employee
        try:
            employee = Employee.objects.get(id=value)
            today = date.today()
            
            try:
                attendance = AttendanceRecord.objects.get(employee=employee, date=today)
                if not attendance.is_clocked_in:
                    raise serializers.ValidationError("Employee is not clocked in today")
            except AttendanceRecord.DoesNotExist:
                raise serializers.ValidationError("No attendance record found for today")
            
            return employee
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found")
    
    def validate_timestamp(self, value):
        """Validate timestamp"""
        if value and value > timezone.now():
            raise serializers.ValidationError("Clock-out time cannot be in the future")
        return value
    
    def create(self, validated_data):
        """Clock out the employee"""
        employee = validated_data['employee']
        today = validated_data.get('timestamp', timezone.now()).date()
        
        try:
            attendance = AttendanceRecord.objects.get(employee=employee, date=today)
        except AttendanceRecord.DoesNotExist:
            raise serializers.ValidationError("No attendance record found for today")
        
        # Set break duration if provided
        if 'break_duration' in validated_data:
            attendance.break_duration = validated_data['break_duration']
        
        # Clock out
        attendance.clock_out(
            timestamp=validated_data.get('timestamp'),
            location=validated_data.get('location')
        )
        
        if validated_data.get('notes'):
            current_notes = attendance.notes or ""
            attendance.notes = f"{current_notes}\nClock-out: {validated_data['notes']}"
            attendance.save()
        
        return attendance


class AttendanceHistorySerializer(serializers.ModelSerializer):
    """Serializer for attendance history"""
    
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department = serializers.CharField(source='employee.department.name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'date', 'employee_name', 'employee_id', 'department',
            'clock_in_time', 'clock_out_time', 'total_hours', 'status',
            'is_overtime', 'overtime_hours', 'break_duration', 'notes'
        ]


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    total_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    average_hours = serializers.DecimalField(max_digits=5, decimal_places=2)
    overtime_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class AttendanceSettingsSerializer(serializers.ModelSerializer):
    """Serializer for attendance settings"""
    
    class Meta:
        model = AttendanceSettings
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Backward compatibility
class AttendanceSerializer(AttendanceRecordSerializer):
    """Backward compatibility alias"""
    pass