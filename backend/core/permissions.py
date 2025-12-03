from rest_framework import permissions


class IsHROrAdmin(permissions.BasePermission):
    """Permission for HR and Admin users only"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_hr


class IsManagerOrAbove(permissions.BasePermission):
    """Permission for Manager, HR and Admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager


class IsOwnerOrHR(permissions.BasePermission):
    """Permission for object owner or HR/Admin"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_hr:
            return True
        
        # Check if user is the owner based on different model types
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'employee'):
            return obj.employee.user == request.user
        elif isinstance(obj, request.user.__class__):
            return obj == request.user
        
        return False


class IsEmployeeOrManager(permissions.BasePermission):
    """Permission for employee's own data or their manager/HR"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # HR can access everything
        if user.is_hr:
            return True
        
        # Employee can access own data
        if hasattr(obj, 'user') and obj.user == user:
            return True
        elif hasattr(obj, 'employee') and obj.employee.user == user:
            return True
        
        # Manager can access subordinates' data
        if user.role == 'MANAGER' and hasattr(obj, 'employee'):
            return obj.employee.manager and obj.employee.manager.user == user
        
        return False


class CanApproveLeave(permissions.BasePermission):
    """Permission to approve leave requests"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # HR can approve any leave
        if user.is_hr:
            return True
        
        # Manager can approve subordinates' leaves
        if user.role == 'MANAGER' and hasattr(obj, 'employee'):
            return obj.employee.manager and obj.employee.manager.user == user
        
        return False