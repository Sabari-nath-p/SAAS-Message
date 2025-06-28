from django.db import models
from clients.models import Client
from core.models import SoftDeleteModel
import templates
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
    INTERVAL_CHOICES = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'), 
        ('days', 'Days'),
        ('weeks', 'Weeks'),
    ]
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    template = models.ForeignKey(MessageTemplate, null=True, blank=True, on_delete=models.CASCADE)
    
    # Changed from interval_days to:
    interval_number = models.PositiveIntegerField(default=1)
    interval_type = models.CharField(
        max_length=10, 
        choices=INTERVAL_CHOICES, 
        default='days'
    )
    
    next_send_at = models.DateTimeField()
    last_sent_at = models.DateTimeField(null=True, blank=True)
    
    def calculate_next_send(self):
        from django.utils import timezone
        from datetime import timedelta
        
        mapping = {
            'minutes': timedelta(minutes=self.interval_number),
            'hours': timedelta(hours=self.interval_number),
            'days': timedelta(days=self.interval_number),
            'weeks': timedelta(weeks=self.interval_number),
        }
        return timezone.now() + mapping[self.interval_type]
    
    def save(self, *args, **kwargs):
        if not self.next_send_at:
            self.next_send_at = self.calculate_next_send()
        super().save(*args, **kwargs)

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