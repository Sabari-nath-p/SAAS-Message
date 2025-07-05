# messaging/admin.py
from django.contrib import admin
from .models import Contact, RecurringMessage

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'client', 'is_active')
    list_filter = ('client', 'is_active')
    search_fields = ('name', 'phone')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client__clientuser__user=request.user)

@admin.register(RecurringMessage)
class RecurringMessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'interval_display', 'next_send_at')
    
    def interval_display(self, obj):
        return f"Every {obj.interval_number} {obj.interval_type}"
    interval_display.short_description = "Frequency"