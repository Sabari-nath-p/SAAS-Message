# clients/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_client_admin', 'is_active')
    list_filter = ('is_client_admin',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(clientuser__client__clientuser__user=request.user)

#admin.site.unregister(User)  # Unregister default User
admin.site.register(User, CustomUserAdmin)