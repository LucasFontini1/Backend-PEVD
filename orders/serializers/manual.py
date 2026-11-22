import re

from rest_framework import serializers

from orders.serializers.address import AddressSerializer
from orders.serializers.checkout import LineSerializer


class ManualOrderSerializer(serializers.Serializer):
    customer_name = serializers.CharField(min_length=2, max_length=160)
    customer_phone = serializers.CharField(max_length=20)
    customer_email = serializers.EmailField(required=False, allow_blank=True, default='')
    items = LineSerializer(many=True, min_length=1, max_length=40)
    fulfillment_type = serializers.ChoiceField(choices=['pickup', 'delivery'])
    scheduled_at = serializers.DateTimeField()
    address = AddressSerializer(required=False)
    notes = serializers.CharField(max_length=1000, allow_blank=True, required=False, default='')
    idempotency_key = serializers.UUIDField()

    def validate_customer_phone(self, value):
        digits = re.sub(r'\D', '', value)
        if not 10 <= len(digits) <= 13:
            raise serializers.ValidationError('Informe DDD e telefone com 10 a 13 dígitos.')
        return digits

    def validate(self, attrs):
        if attrs['fulfillment_type'] == 'delivery' and not attrs.get('address'):
            raise serializers.ValidationError({'address': 'Endereço completo obrigatório para entrega.'})
        return attrs
