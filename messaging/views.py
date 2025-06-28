from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from messaging.models import Contact, RecurringMessage, MessageLog
from messaging.serializers import (
    ContactSerializer,
    RecurringMessageSerializer,
    MessageLogSerializer,
    CreateRecurringMessageSerializer,
    UpdateRecurringMessageSerializer
)
from core.permissions import IsClientAdmin
from core.pagination import StandardResultsSetPagination
from payments.utils import create_payment_link
from datetime import timedelta
from django.utils import timezone

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        return Contact.objects.filter(
            client__clientuser__user=self.request.user
        )
    
    def perform_create(self, serializer):
        client = self.request.user.clientuser_set.first().client
        serializer.save(client=client)

class RecurringMessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'contact']
    
    def get_queryset(self):
        return RecurringMessage.objects.filter(
            contact__client__clientuser__user=self.request.user,
            is_deleted=False
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateRecurringMessageSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateRecurringMessageSerializer
        return RecurringMessageSerializer
    
    def perform_create(self, serializer):
        contact = serializer.validated_data['contact']
        client = contact.client
        recurring_message = serializer.save()
        
        # Create initial payment link
        payment_link = create_payment_link(
            client=client,
            amount=recurring_message.amount,
            recurring_message=recurring_message
        )
        
        # Schedule first message
        self._schedule_message(recurring_message, payment_link)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        recurring_message = self.get_object()
        recurring_message.is_active = False
        recurring_message.save()
        return Response({'status': 'message paused'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        recurring_message = self.get_object()
        recurring_message.is_active = True
        recurring_message.next_send_at = timezone.now() + timedelta(days=recurring_message.interval_days)
        recurring_message.save()
        return Response({'status': 'message resumed'})
    
    def _schedule_message(self, recurring_message, payment_link):
        # Implement actual WhatsApp message scheduling here
        # This would integrate with the WhatsApp Business API
        pass

class MessageLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return MessageLog.objects.filter(
            recurring_message__contact__client__clientuser__user=self.request.user
        )