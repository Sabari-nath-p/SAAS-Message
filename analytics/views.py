from clients.models import SettlementRequest
from messaging.models import Contact, RecurringMessage
from payments.models import Payment
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from analytics.models import ClientAnalytics
from .serialzers import ClientAnalyticsSerializer
from clients.permissions import IsClientAdmin
from clients.pagination import StandardResultsSetPagination
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.utils import timezone

from templates.models import MessageTemplate

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        client = request.user.clientuser_set.first().client
        
        # Total contacts
        total_contacts = Contact.objects.filter(client=client).count()
        active_contacts = Contact.objects.filter(client=client, is_active=True).count()
        
        # Total templates
        total_templates = MessageTemplate.objects.filter(client=client).count()
        active_templates = MessageTemplate.objects.filter(client=client, is_active=True).count()
        
        # Total recurring messages
        total_messages = RecurringMessage.objects.filter(
            contact__client=client,
            is_deleted=False
        ).count()
        active_messages = RecurringMessage.objects.filter(
            contact__client=client,
            is_active=True,
            is_deleted=False
        ).count()
        
        # Payment stats
        payment_stats = Payment.objects.filter(
            recurring_message__contact__client=client,
            status='paid'
        ).aggregate(
            total_amount=Sum('amount'),
            total_payments=Count('id')
        )
        
        # Pending settlements
        pending_settlements = SettlementRequest.objects.filter(
            client=client,
            status='pending'
        ).aggregate(
            total_amount=Sum('amount')
        )
        
        return Response({
            'total_contacts': total_contacts,
            'active_contacts': active_contacts,
            'total_templates': total_templates,
            'active_templates': active_templates,
            'total_messages': total_messages,
            'active_messages': active_messages,
            'total_amount_collected': payment_stats['total_amount'] or 0,
            'total_payments_received': payment_stats['total_payments'] or 0,
            'pending_settlement_amount': pending_settlements['total_amount'] or 0
        })
    
    @action(detail=False, methods=['get'])
    def time_series(self, request):
        client = request.user.clientuser_set.first().client
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        analytics = ClientAnalytics.objects.filter(
            client=client,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        serializer = ClientAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)