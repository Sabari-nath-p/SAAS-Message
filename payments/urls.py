from .views import PaymentViewSet, PaymentWebhookView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')
urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    # Add any additional payment-related URLs here
]
