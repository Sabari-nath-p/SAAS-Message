import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def send_whatsapp_message(client, phone_number, message, template=None):
    if client.uses_own_whatsapp:
        # Use client's own WhatsApp Business API credentials
        access_token = client.whatsapp_access_token
        business_id = client.whatsapp_business_id
    else:
        # Use platform's WhatsApp Business API credentials
        access_token = settings.WHATSAPP_ACCESS_TOKEN
        business_id = settings.WHATSAPP_BUSINESS_ID
    
    url = f"https://graph.facebook.com/v13.0/{business_id}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template" if template else "text",
    }
    
    if template:
        payload["template"] = {
            "name": template,
            "language": {
                "code": "en"
            }
        }
    else:
        payload["text"] = {
            "body": message
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Handle error
        raise e

def schedule_recurring_messages():
    from messaging.models import RecurringMessage
    from payments.utils import create_payment_link
    
    now = timezone.now()
    due_messages = RecurringMessage.objects.filter(
        is_active=True,
        next_send_at__lte=now,
        is_deleted=False
    )
    
    for message in due_messages:
        try:
            # Create new payment link
            payment_link = create_payment_link(
                client=message.contact.client,
                amount=message.amount,
                recurring_message=message
            )
            
            # Prepare message with payment link
            message_text = f"{message.custom_body or message.template.body}\n\nPayment Link: {payment_link}"
            
            # Send WhatsApp message
            response = send_whatsapp_message(
                client=message.contact.client,
                phone_number=message.contact.phone,
                message=message_text
            )
            
            # Update message log
            MessageLog.objects.create(
                recurring_message=message,
                status='sent',
                whatsapp_message_id=response.get('messages', [{}])[0].get('id')
            )
            
            # Update next send time
            message.last_sent_at = now
            message.next_send_at = now + timedelta(days=message.interval_days)
            message.save()
            
        except Exception as e:
            # Log failed attempt
            MessageLog.objects.create(
                recurring_message=message,
                status='failed',
                error_message=str(e)
            )