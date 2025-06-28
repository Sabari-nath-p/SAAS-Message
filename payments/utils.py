import razorpay
from django.conf import settings
from datetime import datetime, timedelta

def get_razorpay_client(client):
    if client.uses_own_razorpay and client.razorpay_key_id and client.razorpay_key_secret:
        return razorpay.Client(auth=(client.razorpay_key_id, client.razorpay_key_secret))
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment_link(client, amount, recurring_message=None):
    razorpay_client = get_razorpay_client(client)
    
    # Create order
    order_data = {
        'amount': int(amount * 100),  # Razorpay expects amount in paise
        'currency': 'INR',
        'payment_capture': 1,
        'notes': {
            'recurring_message_id': str(recurring_message.id) if recurring_message else '',
            'client_id': str(client.id)
        }
    }
    
    order = razorpay_client.order.create(data=order_data)
    
    # Create payment link
    payment_link_data = {
        'amount': int(amount * 100),
        'currency': 'INR',
        'accept_partial': False,
        'description': f'Payment for recurring message',
        'customer': {
            'name': recurring_message.contact.name if recurring_message else '',
            'contact': recurring_message.contact.phone if recurring_message else '',
            'email': recurring_message.contact.email if recurring_message and recurring_message.contact.email else ''
        },
        'notify': {
            'sms': True,
            'email': True
        },
        'reminder_enable': True,
        'notes': order_data['notes'],
        'callback_url': settings.PAYMENT_CALLBACK_URL,
        'callback_method': 'get'
    }
    
    payment_link = razorpay_client.payment_link.create(data=payment_link_data)
    
    # Save payment record
    if recurring_message:
        payment = Payment.objects.create(
            recurring_message=recurring_message,
            razorpay_order_id=order['id'],
            amount=amount,
            currency='INR',
            status='created',
            payment_link=payment_link['short_url']
        )
    
    return payment_link['short_url']