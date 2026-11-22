from rest_framework import serializers

from support.models import ContactInquiry, FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'sort_order', 'published']
        read_only_fields = ['id']


class PublicFAQSerializer(FAQSerializer):
    class Meta(FAQSerializer.Meta):
        fields = ['id', 'question', 'answer', 'sort_order']


class ContactSerializer(serializers.ModelSerializer):
    consent = serializers.BooleanField(write_only=True)
    website = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=200)

    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'subject', 'message', 'consent', 'website']
        extra_kwargs = {
            'name': {'min_length': 2}, 'subject': {'min_length': 4},
            'message': {'min_length': 12, 'max_length': 3000},
        }

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError('Confirme o envio para atendimento.')
        return value

    def create(self, validated_data):
        validated_data.pop('consent', None)
        validated_data.pop('website', None)
        return super().create(validated_data)
