from .views import ContactViewSet, RecurringMessageViewSet, MessageLogViewSet

from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register(r'recurring-messages', RecurringMessageViewSet, basename='recurring-messages')
router.register(r'message-logs', MessageLogViewSet, basename='message-logs')    

urlpatterns = [
    path('', include(router.urls)),
    path('contacts/<int:contact_id>/recurring-messages/', RecurringMessageViewSet.as_view({'get': 'list'}), name='contact-recurring-messages'),
    path('contacts/<int:contact_id>/recurring-messages/<int:pk>/', RecurringMessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='contact-recurring-message-detail'), 
    path('contacts/<int:contact_id>/message-logs/', MessageLogViewSet.as_view({'get': 'list'}), name='contact-message-logs'),
    path('contacts/<int:contact_id>/message-logs/<int:pk>/', MessageLogViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='contact-message-log-detail'),
    path('recurring-messages/<int:recurring_message_id>/message-logs/', MessageLogViewSet.as_view({'get': 'list'}), name='recurring-message-logs'),
    path('recurring-messages/<int:recurring_message_id>/message-logs/<int:pk>/', MessageLogViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='recurring-message-log-detail'),
]       
