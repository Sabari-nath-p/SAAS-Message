from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin

class IsClientAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_super_admin:
            return True
        
        return ClientUser.objects.filter(
            user=request.user,
            is_admin=True
        ).exists()