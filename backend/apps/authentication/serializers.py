from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'role']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # Set default approval status for new users
        if validated_data.get('role') == 'EMPLOYEE':
            validated_data['is_approved'] = False
            validated_data['approval_status'] = 'PENDING'
        else:
            # HR and Admin roles auto-approved
            validated_data['is_approved'] = True
            validated_data['approval_status'] = 'APPROVED'
        
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            # Check if user can login (approval system)
            if not user.can_login:
                if user.approval_status == 'PENDING':
                    raise serializers.ValidationError(
                        'Your account is pending approval. Please wait for HR to approve your account.'
                    )
                elif user.approval_status == 'REJECTED':
                    reason = user.rejection_reason or 'No reason provided'
                    raise serializers.ValidationError(
                        f'Your account was rejected. Reason: {reason}. Please contact HR for more information.'
                    )
                else:
                    raise serializers.ValidationError('Your account is not approved for login')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    full_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 
            'phone', 'is_active', 'date_joined', 'is_approved', 'approval_status', 
            'approved_by', 'approved_by_name', 'approved_at', 'rejection_reason'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined', 'is_approved', 'approval_status', 
            'approved_by', 'approved_at', 'rejection_reason'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password fields didn't match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value