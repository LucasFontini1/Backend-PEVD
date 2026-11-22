from rest_framework.routers import DefaultRouter

from support.views.admin import AdminContactViewSet, AdminFAQViewSet
from support.views.public import PublicFAQViewSet
from support.views.quotes import AdminQuoteViewSet, ClientQuoteViewSet
from support.views.tickets import AdminTicketViewSet, ClientTicketViewSet

public_router = DefaultRouter()
public_router.register('faqs', PublicFAQViewSet, basename='faqs')

client_router = DefaultRouter()
client_router.register('support/tickets', ClientTicketViewSet, basename='support-tickets')
client_router.register('quotes', ClientQuoteViewSet, basename='quotes')

admin_router = DefaultRouter()
admin_router.register('faqs', AdminFAQViewSet, basename='admin-faqs')
admin_router.register('contact', AdminContactViewSet, basename='admin-contact')
admin_router.register('support/tickets', AdminTicketViewSet, basename='admin-support-tickets')
admin_router.register('quotes', AdminQuoteViewSet, basename='admin-quotes')
