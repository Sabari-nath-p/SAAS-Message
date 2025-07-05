# templates/admin.py
from django.contrib import admin
from .models import MessageTemplate

@admin.register(MessageTemplate)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'is_active')
    list_editable = ('is_active',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client__clientuser__user=request.user)