from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Custom permission to allow only Admins access
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
    
class IsSuperUser(BasePermission):
    """
    Custom permission to allow only Superusers access
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
    
class IsWarehouse(BasePermission):
    """
    Custom permission to allow only Warehouse staff access
    """

    def has_permission(self, request, view):
        return request.user.is_warehouse and request.user.is_authenticated
    