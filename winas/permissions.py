# performance_appraisal/permissions.py
from rest_framework import permissions

class IsCEO(permissions.BasePermission):
    """
    Custom permission to only allow users with 'CEO' role.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # A CEO is typically also a superuser/staff, but explicitly check role
        return request.user.is_superuser and \
               (hasattr(request.user, 'role') and request.user.role and request.user.role.role_name == 'CEO')

class IsAdminOrCEO(permissions.BasePermission):
    """
    Custom permission to only allow users with 'Admin' or 'CEO' roles.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.is_staff or request.user.is_superuser or \
               (hasattr(request.user, 'role') and request.user.role and \
                request.user.role.role_name in ['Admin', 'CEO'])

class IsSupervisorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow supervisors or admin users.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.is_superuser:
            return True

        return hasattr(request.user, 'role') and request.user.role and \
               request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users.
    For retrieving/updating their own performance data.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return True

        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user

        return obj.user == request.user

class IsDepartmentSupervisor(permissions.BasePermission):
    """
    Custom permission to allow supervisors to manage employees/data within their department.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Admins/Superusers can bypass this
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check if the user is a supervisor and has a department assigned
        is_supervisor = hasattr(request.user, 'role') and request.user.role and \
                        request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM']
        has_department = hasattr(request.user, 'department') and request.user.department is not None

        return is_supervisor and has_department

    def has_object_permission(self, request, view, obj):
        # Admins/Superusers can bypass this
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return True

        # Check if the requesting user is a supervisor for the object's department
        if hasattr(obj, 'department') and obj.department: # For User objects
            return request.user.department == obj.department
        elif hasattr(obj, 'user') and hasattr(obj.user, 'department') and obj.user.department: # For performance/training objects
            return request.user.department == obj.user.department
        
        # If the object doesn't have a department or associated user with a department,
        # then this permission doesn't apply, or it's implicitly denied if not handled by other permissions.
        return False