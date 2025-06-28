from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from clients.models import Client, ClientUser, SettlementRequest
from clients.serializers import (
    ClientSerializer, 
    ClientUserSerializer,
    SettlementRequestSerializer,
    CreateClientSerializer,
    UpdateClientSerializer
)
from core.permissions import IsSuperAdmin, IsClientAdmin
from core.pagination import StandardResultsSetPagination

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.filter(is_deleted=False)
    permission_classes = [IsSuperAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'uses_own_razorpay', 'uses_own_whatsapp']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateClientSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateClientSerializer
        return ClientSerializer
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        client = self.get_object()
        client.is_active = False
        client.disabled_at = timezone.now()
        client.save()
        return Response({'status': 'client disabled'})
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        client = self.get_object()
        client.is_active = True
        client.disabled_at = None
        client.save()
        return Response({'status': 'client enabled'})

class ClientUserViewSet(viewsets.ModelViewSet):
    serializer_class = ClientUserSerializer
    permission_classes = [IsSuperAdmin | IsClientAdmin]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        if self.request.user.is_super_admin:
            return ClientUser.objects.all()
        return ClientUser.objects.filter(client__clientuser__user=self.request.user)
    
    def perform_create(self, serializer):
        client_user = serializer.save()
        # Send invitation email if needed
        return super().perform_create(serializer)

class SettlementRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SettlementRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        if self.request.user.is_super_admin:
            return SettlementRequest.objects.filter(is_deleted=False)
        return SettlementRequest.objects.filter(
            client__clientuser__user=self.request.user,
            is_deleted=False
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def approve(self, request, pk=None):
        settlement = self.get_object()
        settlement.status = 'approved'
        settlement.save()
        return Response({'status': 'settlement approved'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def reject(self, request, pk=None):
        settlement = self.get_object()
        settlement.status = 'rejected'
        settlement.save()
        return Response({'status': 'settlement rejected'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def mark_as_processed(self, request, pk=None):
        settlement = self.get_object()
        settlement.status = 'processed'
        settlement.processed_at = timezone.now()
        settlement.save()
        return Response({'status': 'settlement processed'})