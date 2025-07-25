from __future__ import absolute_import
from dbm import _error
import os

from pandas import crosstab
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('whatsapp_saas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Schedule recurring messages check every 5 minutes
    sender.add_periodic_task(
        300.0,  # Every 5 minutes
        check_recurring_messages.s(),
        name='check-recurring-messages'
    )
    
    # Schedule daily analytics at midnight
    sender.add_periodic_task(
        crosstab(hour=0, minute=0),
        generate_daily_analytics.s(),
        name='generate-daily-analytics'
    )

@app.task
def check_recurring_messages():
    from django.utils import timezone
    from messaging.models import RecurringMessage
    
    now = timezone.now()
    messages = RecurringMessage.objects.filter(
        is_active=True,
        next_send_at__lte=now,
        is_deleted=False
    )
    
    for message in messages:
        try:
            # Process message (send WhatsApp + create payment link)
            # process_message.delay(message.id)
            
            # Update next send time using the model's method
            message.last_sent_at = now
            message.next_send_at = message.calculate_next_send()
            message.save()
            
        except Exception as e:
            _error.delay(message.id, str(e))

@app.task
def generate_daily_analytics():
    from analytics.models import ClientAnalytics
    from messaging.models import Contact, RecurringMessage, MessageLog
    from payments.models import Payment
    from datetime import date
    
    today = date.today()
    
    for client in Client.objects.filter(is_active=True):
        # Get counts
        active_contacts = Contact.objects.filter(client=client, is_active=True).count()
        active_messages = RecurringMessage.objects.filter(
            contact__client=client,
            is_active=True,
            is_deleted=False
        ).count()
        
        # Get message stats
        messages_sent = MessageLog.objects.filter(
            recurring_message__contact__client=client,
            status='sent',
            created_at__date=today
        ).count()
        
        # Get payment stats
        payments_today = Payment.objects.filter(
            recurring_message__contact__client=client,
            status='paid',
            updated_at__date=today
        ).aggregate(
            total_amount=Sum('amount'),
            total_payments=Count('id')
        )
        
        # Create or update analytics record
        ClientAnalytics.objects.update_or_create(
            client=client,
            date=today,
            defaults={
                'active_users': active_contacts,
                'messages_sent': messages_sent,
                'payments_received': payments_today['total_payments'] or 0,
                'amount_collected': payments_today['total_amount'] or 0,
                'templates_used': active_messages
            }
        )