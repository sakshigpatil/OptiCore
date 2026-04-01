from rest_framework import permissions


class HasRolePermission(permissions.BasePermission):
    """Permission class that checks user roles"""

    def has_permission(self, request, view):
        user = request.user

        # Allow access if user is authenticated and has a role
        if not user.is_authenticated or not hasattr(user, 'role'):
            return False

        # Define role hierarchy
        role_permissions = {
            'ADMIN_HR': ['view_all_employees', 'view_all_departments', 'view_attendance_data',
                        'view_leave_data', 'view_payroll_data', 'view_project_data',
                        'view_analytics', 'export_data'],
            'MANAGER': ['view_team_employees', 'view_department_stats', 'view_team_attendance',
                       'view_team_leaves', 'view_basic_payroll', 'view_team_projects',
                       'view_team_performance', 'export_team_data'],
            'EMPLOYEE': ['view_own_profile', 'view_own_attendance', 'view_own_leaves',
                        'view_basic_payroll', 'export_own_data']
        }

        # Store permissions on user for easy access
        user.permissions = role_permissions.get(user.role, [])
        return True


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