from .views import ClientViewSet, ClientUserViewSet, SettlementRequestViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'client-users', ClientUserViewSet, basename='client-users')
router.register(r'settlement-requests', SettlementRequestViewSet, basename='settlement-requests')
urlpatterns = [
    path('', include(router.urls)),
    path('clients/<int:client_id>/settlement-requests/', SettlementRequestViewSet.as_view({'get': 'list'}), name='client-settlement-requests'),
    path('clients/<int:client_id>/settlement-requests/<int:pk>/', SettlementRequestViewSet.as_view({'get': 'retrieve', 'post': 'update', 'delete': 'destroy'}), name='client-settlement-request-detail'),
    path('clients/<int:client_id>/users/', ClientUserViewSet.as_view({'get': 'list', 'post': 'create'}), name='client-users-list'),
    path('clients/<int:client_id>/users/<int:pk>/', ClientUserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='client-user-detail'),
    path('clients/<int:client_id>/disable/', ClientViewSet.as_view({'post': 'disable'}), name='client-disable'),
    path('clients/<int:client_id>/enable/', ClientViewSet.as_view({'post': 'enable'}), name='client-enable'),   
]