from rest_framework import serializers

from orders.models import Order
from support.models import SupportMessage, SupportTicket


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ['id', 'sender', 'body', 'created_at']
        read_only_fields = fields


class TicketSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = ['id', 'user', 'order', 'subject', 'status', 'created_at', 'updated_at', 'messages']
        read_only_fields = fields


class TicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(min_length=4, max_length=180)
    message = serializers.CharField(min_length=5, max_length=4000)
    order_id = serializers.IntegerField(min_value=1, required=False)

    def validate_order_id(self, value):
        request = self.context['request']
        if not Order.objects.filter(pk=value, user=request.user).exists():
            raise serializers.ValidationError('Pedido não encontrado.')
        return value


class ReplySerializer(serializers.Serializer):
    message = serializers.CharField(min_length=1, max_length=4000)


class AdminReplySerializer(ReplySerializer):
    close = serializers.BooleanField(required=False, default=False)
