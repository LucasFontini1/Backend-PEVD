from rest_framework.routers import DefaultRouter

from orders.views.admin import AdminOrderViewSet, BlockedDateViewSet, DeliveryZoneViewSet, HourViewSet
from orders.views.client import AddressViewSet, OrderViewSet

client_router = DefaultRouter()
client_router.register('addresses', AddressViewSet, basename='addresses')
client_router.register('orders', OrderViewSet, basename='orders')

admin_router = DefaultRouter()
admin_router.register('orders', AdminOrderViewSet, basename='admin-orders')
admin_router.register('delivery-zones', DeliveryZoneViewSet, basename='admin-delivery-zones')
admin_router.register('business-hours', HourViewSet, basename='admin-business-hours')
admin_router.register('blocked-dates', BlockedDateViewSet, basename='admin-blocked-dates')
