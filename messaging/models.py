from django.db import models
from clients.models import Client
from templates.models import MessageTemplate

class Contact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('client', 'phone')
    
    def __str__(self):
        return f"{self.name} ({self.phone})"

class RecurringMessage(SoftDeleteModel):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE, blank=True, null=True)
    custom_title = models.TextField(blank=True, null=True)
    custom_body = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interval_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    next_send_at = models.DateTimeField()
    last_sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.contact} - Every {self.interval_days} days"

class MessageLog(models.Model):
    recurring_message = models.ForeignKey(RecurringMessage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ])
    whatsapp_message_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.recurring_message} - {self.status}"