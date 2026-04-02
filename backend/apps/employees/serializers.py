from rest_framework import serializers
from .models import Employee, Department, EmployeeDocument
from apps.authentication.serializers import UserSerializer
from apps.authentication.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer"""
    head_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head', 'head_name', 'employee_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'head_name', 'employee_count']
    
    def get_head_name(self, obj):
        return obj.head.user.get_full_name() if obj.head else None
    
    def get_employee_count(self, obj):
        return obj.employee_set.filter(status='ACTIVE').count()


class EmployeeSerializer(serializers.ModelSerializer):
    """Employee serializer"""
    user_details = UserSerializer(source='user', read_only=True)
    department_name = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'user', 'user_details', 'department', 'department_name',
            'manager', 'manager_name', 'position', 'hire_date', 'termination_date',
            'salary', 'address', 'date_of_birth', 'profile_picture', 'status',
            'emergency_contact_name', 'emergency_contact_phone', 'years_of_service',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'years_of_service']
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_manager_name(self, obj):
        return obj.manager.user.get_full_name() if obj.manager else None
    
    def get_years_of_service(self, obj):
        if obj.hire_date:
            from datetime import date
            today = date.today()
            years = today.year - obj.hire_date.year
            if today.month < obj.hire_date.month or (today.month == obj.hire_date.month and today.day < obj.hire_date.day):
                years -= 1
            return years
        return 0


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Employee creation serializer with user creation"""
    user_data = serializers.DictField(required=True, write_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'user_data', 'department', 'manager', 'position',
            'hire_date', 'salary', 'address', 'date_of_birth', 'emergency_contact_name',
            'emergency_contact_phone'
        ]
    
    def validate_user_data(self, value):
        """Validate user data fields"""
        required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
        errors = {}
        
        for field in required_fields:
            if not value.get(field):
                errors[field] = f'{field.replace("_", " ").title()} is required'
        
        # Check if username exists
        if value.get('username'):
            from apps.authentication.models import User
            if User.objects.filter(username=value['username']).exists():
                errors['username'] = 'A user with that username already exists.'
        
        # Check if email exists
        if value.get('email'):
            from apps.authentication.models import User
            if User.objects.filter(email=value['email']).exists():
                errors['email'] = 'A user with that email already exists.'
        
        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if value.get('email') and not re.match(email_pattern, value['email']):
            errors['email'] = 'Enter a valid email address.'
        
        # Validate password length
        if value.get('password') and len(value['password']) < 6:
            errors['password'] = 'Password must be at least 6 characters long.'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return value
    
    def create(self, validated_data):
        from apps.authentication.models import User
        user_data = validated_data.pop('user_data')
        
        # Create user with proper password hashing
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password'],
            role=user_data.get('role', 'EMPLOYEE'),
            phone=user_data.get('phone'),
            is_approved=True,  # Auto-approve HR-created employees
            approval_status='APPROVED'
        )
        
        # Create employee
        employee = Employee.objects.create(user=user, **validated_data)
        return employee


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Employee profile serializer for self-updates"""
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'user_details', 'address', 'date_of_birth',
            'profile_picture', 'emergency_contact_name', 'emergency_contact_phone'
        ]
        read_only_fields = ['id', 'employee_id', 'user_details']


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Employee update serializer (HR updates)"""
    user_role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta:
        model = Employee
        fields = [
            'department', 'manager', 'position', 'hire_date', 'termination_date',
            'salary', 'address', 'date_of_birth', 'profile_picture', 'status',
            'emergency_contact_name', 'emergency_contact_phone', 'user_role'
        ]

    def update(self, instance, validated_data):
        user_role = validated_data.pop('user_role', None)
        if user_role and instance.user:
            instance.user.role = user_role
            instance.user.save(update_fields=['role'])
        return super().update(instance, validated_data)


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Employee document serializer"""
    employee_name = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'employee', 'employee_name', 'document_type', 'title', 'document_file',
            'document_url', 'description', 'issue_date', 'expiry_date', 'uploaded_by',
            'uploaded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_name', 'uploaded_by_name', 'document_url']

    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name() if obj.employee and obj.employee.user else None

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else None

    def get_document_url(self, obj):
        if not obj.document_file:
            return None
        request = self.context.get('request')
        url = obj.document_file.url
        return request.build_absolute_uri(url) if request else url


class EmployeeDocumentCreateSerializer(serializers.ModelSerializer):
    """Employee document create/update serializer"""

    class Meta:
        model = EmployeeDocument
        fields = [
            'employee', 'document_type', 'title', 'document_file',
            'description', 'issue_date', 'expiry_date'
        ]