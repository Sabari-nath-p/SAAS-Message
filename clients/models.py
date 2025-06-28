from django.db import models
from core.models import SoftDeleteModel, User

class Client(SoftDeleteModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uses_own_razorpay = models.BooleanField(default=False)
    razorpay_key_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_key_secret = models.CharField(max_length=255, blank=True, null=True)
    uses_own_whatsapp = models.BooleanField(default=False)
    whatsapp_business_id = models.CharField(max_length=255, blank=True, null=True)
    whatsapp_access_token = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name

class ClientUser(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('client', 'user')

class SettlementRequest(SoftDeleteModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    ], default='pending')
    request_note = models.TextField(blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.client} - {self.amount}"