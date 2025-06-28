from rest_framework import serializers
from analytics.models import ClientAnalytics

class ClientAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAnalytics
        fields = [
            'date',
            'amount_collected',
            'payments_received'
        ]
