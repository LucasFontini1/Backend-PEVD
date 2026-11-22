from django.contrib import admin

from orders.models import (
    BlockedDate, BusinessHour, CustomerAddress, DeliveryZone, Order, OrderItem,
    OrderItemOption, OrderStatusHistory,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name_snapshot', 'unit_price', 'quantity', 'subtotal']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['public_id', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'fulfillment_type']
    search_fields = ['public_id', 'user__email']
    readonly_fields = [
        'user', 'public_id', 'idempotency_key', 'request_digest', 'subtotal',
        'shipping', 'total', 'address_snapshot', 'created_at',
    ]
    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register([CustomerAddress, BusinessHour, BlockedDate, DeliveryZone])
admin.site.register([OrderItemOption, OrderStatusHistory])
