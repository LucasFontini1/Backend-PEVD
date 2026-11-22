import re

from rest_framework import serializers

from orders.models import CustomerAddress


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'label', 'zip_code', 'street', 'number',
            'complement', 'district', 'city', 'state',
        ]

    def validate_zip_code(self, value):
        digits = re.sub(r'\D', '', value)
        if len(digits) != 8:
            raise serializers.ValidationError('CEP deve conter oito dígitos.')
        return digits

    def validate_state(self, value):
        if not re.fullmatch(r'[A-Za-z]{2}', value):
            raise serializers.ValidationError('Informe UF com duas letras.')
        return value.upper()
