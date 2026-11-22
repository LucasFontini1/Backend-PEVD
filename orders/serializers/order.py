from rest_framework import serializers

from orders.models import Order, OrderItem, OrderItemOption, OrderStatusHistory
from orders.services.customer_identity import customer_display_name


class SnapshotOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemOption
        fields = ['group_name_snapshot', 'option_name_snapshot', 'additional_price_snapshot']


class SnapshotItemSerializer(serializers.ModelSerializer):
    options = SnapshotOptionSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_name_snapshot', 'unit_price', 'quantity', 'subtotal', 'options']


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['previous_status', 'new_status', 'reason', 'changed_at']


class OrderSerializer(serializers.ModelSerializer):
    items = SnapshotItemSerializer(many=True, read_only=True)
    history = HistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'source', 'customer_name', 'customer_phone', 'public_id', 'status', 'payment_status', 'fulfillment_type',
            'scheduled_at', 'notes', 'address_snapshot', 'shipping',
            'subtotal', 'total', 'created_at', 'items', 'history',
        ]


class AdminOrderSerializer(OrderSerializer):
    customer_display_name = serializers.SerializerMethodField()

    def get_customer_display_name(self, obj):
        return customer_display_name(obj)

    class Meta(OrderSerializer.Meta):
        fields = ['id', 'user', 'customer_display_name', *OrderSerializer.Meta.fields]
