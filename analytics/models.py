from django.db import models
from clients.models import Client

class ClientAnalytics(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    active_users = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    payments_received = models.PositiveIntegerField(default=0)
    amount_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    templates_used = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('client', 'date')
    
    def __str__(self):
        return f"{self.client} - {self.date}"