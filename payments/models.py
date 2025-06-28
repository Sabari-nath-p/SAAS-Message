from django.db import models
from clients.models import Client
from messaging.models import RecurringMessage

class Payment(models.Model):
    recurring_message = models.ForeignKey(RecurringMessage, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=[
        ('created', 'Created'),
        ('attempted', 'Attempted'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='created')
    payment_link = models.URLField()
    payment_link_status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.recurring_message} - {self.amount}"

class PaymentWebhookLog(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    payload = models.JSONField()
    event_type = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"