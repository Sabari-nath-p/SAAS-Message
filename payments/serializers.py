from rest_framework import serializers
from payments.models import Payment, PaymentWebhookLog

class PaymentSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='recurring_message.contact.name', read_only=True)
    client_name = serializers.CharField(source='recurring_message.contact.client.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'recurring_message', 'contact_name', 'client_name',
            'razorpay_payment_id', 'razorpay_order_id', 'amount',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PaymentWebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentWebhookLog
        fields = [
            'id', 'client', 'event_type', 'razorpay_payment_id',
            'razorpay_order_id', 'payload', 'created_at'
        ]
        read_only_fields = ['created_at']
