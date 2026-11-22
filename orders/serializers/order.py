from rest_framework import serializers

from orders.models import Order, OrderItem, OrderItemOption, OrderStatusHistory


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
            'public_id', 'status', 'payment_status', 'fulfillment_type',
            'scheduled_at', 'notes', 'address_snapshot', 'shipping',
            'subtotal', 'total', 'created_at', 'items', 'history',
        ]


class AdminOrderSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = ['id', 'user', *OrderSerializer.Meta.fields]
