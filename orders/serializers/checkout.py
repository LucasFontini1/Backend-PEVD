from rest_framework import serializers


class LineSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    selected_option_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False, default=list, max_length=30,
    )

    def validate_selected_option_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Opções repetidas.')
        return value


class CheckoutSerializer(serializers.Serializer):
    items = LineSerializer(many=True, min_length=1, max_length=40)
    fulfillment_type = serializers.ChoiceField(choices=['pickup', 'delivery'])
    scheduled_at = serializers.DateTimeField()
    address_id = serializers.IntegerField(min_value=1, required=False)
    notes = serializers.CharField(max_length=1000, allow_blank=True, required=False, default='')
    idempotency_key = serializers.UUIDField(required=False)
    quote_hash = serializers.CharField(max_length=64, required=False)

    def validate(self, data):
        if data['fulfillment_type'] == 'delivery' and not data.get('address_id'):
            raise serializers.ValidationError({'address_id': 'Endereço obrigatório para entrega.'})
        ids = [line['product_id'] for line in data['items']]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError({'items': 'Agrupe quantidades do mesmo produto em uma linha.'})
        return data
