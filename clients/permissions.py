# core/permissions.py

from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'is_super_admin') and request.user.is_super_admin

class IsClientAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'is_client_admin') and request.user.is_client_admin
