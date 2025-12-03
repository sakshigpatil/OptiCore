from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    PasswordChangeSerializer
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AuthViewSet(viewsets.GenericViewSet):
    """Authentication viewset"""
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """User registration"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Different responses based on approval status
            if user.approval_status == 'PENDING':
                return Response({
                    'message': 'Registration successful. Your account is pending approval. You will be able to login once HR approves your account.',
                    'user': UserSerializer(user).data,
                    'approval_status': user.approval_status
                }, status=status.HTTP_201_CREATED)
            else:
                # Auto-approved users (HR/Admin) get tokens immediately
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """User login"""
        logger.info(f"Login attempt - Request data: {request.data}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content type: {request.content_type}")
        
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            logger.info(f"Login successful for user: {user.email}")
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            logger.info(f"Login response: {response_data}")
            return Response(response_data)
        
        logger.error(f"Login failed - Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """User logout"""
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'message': 'Successfully logged out'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset (HR/Admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only HR/Admin can manage users"""
        if self.action in ['list', 'create', 'update', 'destroy', 'pending_approvals', 'approve_user', 'reject_user']:
            permission_classes = [permissions.IsAuthenticated]
            # Add custom permission for HR/Admin only - for now allowing all authenticated users
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get list of users pending approval"""
        # Only HR and Admin can view pending approvals
        if request.user.role not in ['ADMIN_HR', 'MANAGER']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        pending_users = User.objects.filter(approval_status='PENDING')
        serializer = UserSerializer(pending_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_user(self, request, pk=None):
        """Approve a user account"""
        # Only HR and Admin can approve users
        if request.user.role not in ['ADMIN_HR', 'MANAGER']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = self.get_object()
            if user.approval_status != 'PENDING':
                return Response({'error': 'User is not in pending state'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_approved = True
            user.approval_status = 'APPROVED'
            user.approved_by = request.user
            user.approved_at = timezone.now()
            user.save()
            
            return Response({
                'message': 'User approved successfully',
                'user': UserSerializer(user).data
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def reject_user(self, request, pk=None):
        """Reject a user account"""
        # Only HR and Admin can reject users
        if request.user.role not in ['ADMIN_HR', 'MANAGER']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = self.get_object()
            if user.approval_status != 'PENDING':
                return Response({'error': 'User is not in pending state'}, status=status.HTTP_400_BAD_REQUEST)
            
            rejection_reason = request.data.get('rejection_reason', '')
            
            user.is_approved = False
            user.approval_status = 'REJECTED'
            user.approved_by = request.user
            user.approved_at = timezone.now()
            user.rejection_reason = rejection_reason
            user.save()
            
            return Response({
                'message': 'User rejected successfully',
                'user': UserSerializer(user).data
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)