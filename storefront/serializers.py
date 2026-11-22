from rest_framework import serializers

from catalog.serializers import ImagePublicSerializer, validate_image_ownership
from storefront.models import Banner
from uploader.models import Image


class PublicBannerSerializer(serializers.ModelSerializer):
    image = ImagePublicSerializer(read_only=True)

    class Meta:
        model = Banner
        fields = ['id', 'title', 'subtitle', 'image', 'link_path', 'sort_order']
        read_only_fields = fields


class AdminBannerSerializer(serializers.ModelSerializer):
    image = ImagePublicSerializer(read_only=True)
    image_attachment_key = serializers.SlugRelatedField(
        source='image', slug_field='attachment_key', queryset=Image.objects.all(),
        write_only=True, allow_null=True, required=False,
    )

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'image', 'image_attachment_key',
            'link_path', 'is_active', 'sort_order',
        ]

    def validate_image_attachment_key(self, value):
        return validate_image_ownership(value, self.context)

    def validate_link_path(self, value):
        if not value.startswith('/') or value.startswith('//') or '\\' in value:
            raise serializers.ValidationError('Informe um caminho interno começando com /.')
        if '\n' in value or '\r' in value:
            raise serializers.ValidationError('Caminho inválido.')
        return value
