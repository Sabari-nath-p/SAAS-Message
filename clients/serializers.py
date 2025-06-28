from rest_framework import serializers
from clients.models import Client, ClientUser, SettlementRequest
from django.contrib.auth import get_user_model

User = get_user_model()

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'is_active',
            'uses_own_razorpay', 'uses_own_whatsapp',
            'created_at', 'updated_at'
        ]


class CreateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone',
            'uses_own_razorpay', 'uses_own_whatsapp'
        ]


class UpdateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'is_active',
            'uses_own_razorpay', 'uses_own_whatsapp'
        ]


class ClientUserSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ClientUser
        fields = [
            'id', 'user', 'user_email', 'client',
            'role', 'created_at'
        ]
        read_only_fields = ['created_at']


class SettlementRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = SettlementRequest
        fields = [
            'id', 'client', 'client_name', 'amount',
            'status', 'requested_at', 'processed_at',
            'is_deleted'
        ]
        read_only_fields = ['status', 'processed_at']
