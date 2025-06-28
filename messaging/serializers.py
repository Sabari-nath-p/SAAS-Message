from rest_framework import serializers
from .models import RecurringMessage, MessageLog, Contact
from templates.models import MessageTemplate

class RecurringMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringMessage
        fields = '__all__'
        extra_kwargs = {
            'next_send_at': {'read_only': True}
        }

class CreateRecurringMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringMessage
        fields = ['contact', 'template', 'interval_number', 'interval_type', 'amount']


class UpdateRecurringMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringMessage
        fields = ['interval_number', 'interval_type', 'amount']


class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['id', 'contact', 'template', 'status', 'sent_at', 'response']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number', 'email']
