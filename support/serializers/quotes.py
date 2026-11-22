from django.utils import timezone
from rest_framework import serializers

from support.models import CustomQuote


class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomQuote
        fields = ['title', 'details', 'flavor', 'portions', 'desired_date']
        extra_kwargs = {
            'title': {'min_length': 4}, 'details': {'min_length': 10, 'max_length': 4000},
            'portions': {'min_value': 1, 'max_value': 1000},
        }

    def validate_desired_date(self, value):
        if value <= timezone.localdate():
            raise serializers.ValidationError('Informe uma data futura.')
        return value


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomQuote
        fields = [
            'id', 'title', 'details', 'flavor', 'portions', 'desired_date',
            'status', 'proposed_price', 'proposed_details', 'valid_until',
            'accepted_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class QuoteProposalSerializer(serializers.Serializer):
    proposed_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    proposed_details = serializers.CharField(min_length=5, max_length=3000)
    valid_until = serializers.DateTimeField()

    def validate_valid_until(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('A validade deve ser futura.')
        return value
