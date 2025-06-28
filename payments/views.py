from analytics.models import ClientAnalytics
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from payments.models import Payment, PaymentWebhookLog
from payments.serializers import PaymentSerializer, PaymentWebhookLogSerializer
from clients.permissions import IsClientAdmin
from clients.pagination import StandardResultsSetPagination
from datetime import datetime, timedelta
import razorpay
from django.conf import settings
from rest_framework.views import APIView

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Payment.objects.filter(
            recurring_message__contact__client__clientuser__user=self.request.user
        )

class PaymentWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        payload = request.data
        client = self._get_client_from_payload(payload)
        
        # Verify webhook signature
        if not self._verify_webhook_signature(request):
            return Response({'status': 'invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log webhook
        webhook_log = PaymentWebhookLog.objects.create(
            client=client,
            payload=payload,
            event_type=payload.get('event'),
            razorpay_payment_id=payload.get('payload', {}).get('payment', {}).get('entity', {}).get('id'),
            razorpay_order_id=payload.get('payload', {}).get('payment', {}).get('entity', {}).get('order_id')
        )
        
        # Process webhook
        self._process_webhook(payload, client)
        
        return Response({'status': 'success'})
    
    def _get_client_from_payload(self, payload):
        # Implement logic to determine client from payload
        pass
    
    def _verify_webhook_signature(self, request):
        razorpay_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            client.utility.verify_webhook_signature(
                request.body.decode('utf-8'),
                razorpay_signature,
                webhook_secret
            )
            return True
        except:
            return False
    
    def _process_webhook(self, payload, client):
        event = payload.get('event')
        
        if event == 'payment.captured':
            self._handle_payment_captured(payload, client)
        elif event == 'payment.failed':
            self._handle_payment_failed(payload, client)
        # Handle other event types as needed
    
    def _handle_payment_captured(self, payload, client):
        payment_data = payload.get('payload', {}).get('payment', {}).get('entity', {})
        
        try:
            payment = Payment.objects.get(
                razorpay_order_id=payment_data.get('order_id'),
                razorpay_payment_id=payment_data.get('id')
            )
            payment.status = 'paid'
            payment.save()
            
            # Update analytics
            self._update_analytics(client, payment.amount)
            
        except Payment.DoesNotExist:
            pass
    
    def _handle_payment_failed(self, payload, client):
        payment_data = payload.get('payload', {}).get('payment', {}).get('entity', {})
        
        try:
            payment = Payment.objects.get(
                razorpay_order_id=payment_data.get('order_id'),
                razorpay_payment_id=payment_data.get('id')
            )
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    def _update_analytics(self, client, amount):
        # Update daily analytics for the client
        today = datetime.now().date()
        analytics, created = ClientAnalytics.objects.get_or_create(
            client=client,
            date=today,
            defaults={
                'amount_collected': amount,
                'payments_received': 1
            }
        )
        
        if not created:
            analytics.amount_collected += amount
            analytics.payments_received += 1
            analytics.save()