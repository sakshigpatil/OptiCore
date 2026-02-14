from rest_framework import serializers
from .models import LeaveType, LeaveRequest, ResignationRequest
from apps.employees.models import Employee

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class EmployeeBasicSerializer(serializers.ModelSerializer):
    """Basic employee info for leave requests"""
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'user']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email
        }

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    employee_detail = EmployeeBasicSerializer(source='employee', read_only=True)
    leave_type_detail = LeaveTypeSerializer(source='leave_type', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.user.get_full_name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'processed_on', 'employee')

class ResignationRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)

    class Meta:
        model = ResignationRequest
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')