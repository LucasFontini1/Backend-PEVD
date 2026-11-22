from decimal import Decimal

from rest_framework import serializers

from catalog.models import Category, Product, ProductImage, ProductOption, ProductOptionGroup, ShopBrand
from uploader.models import Image


class ImagePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['url', 'description']
        read_only_fields = fields


class CategoryPublicSerializer(serializers.ModelSerializer):
    image = ImagePublicSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'sort_order']
        read_only_fields = fields


class OptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['id', 'name', 'additional_price']
        read_only_fields = fields


class OptionGroupPublicSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptionGroup
        fields = ['id', 'name', 'required', 'multiple', 'options']
        read_only_fields = fields

    def get_options(self, instance):
        return OptionPublicSerializer(instance.options.filter(is_active=True), many=True).data


class ProductImagePublicSerializer(serializers.ModelSerializer):
    image = ImagePublicSerializer(read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'sort_order']
        read_only_fields = fields


class ProductPublicSerializer(serializers.ModelSerializer):
    category = CategoryPublicSerializer(read_only=True)
    images = ProductImagePublicSerializer(read_only=True, many=True)
    option_groups = OptionGroupPublicSerializer(read_only=True, many=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'ingredients', 'allergen_info',
            'conservation_info', 'category', 'price', 'promotional_price', 'effective_price',
            'unit', 'minimum_quantity', 'minimum_lead_hours', 'is_available',
            'is_featured', 'images', 'option_groups',
        ]
        read_only_fields = fields


def validate_image_ownership(image, context):
    if image is None:
        return image
    request = context.get('request')
    if not request or image.owner_id != request.user.pk:
        raise serializers.ValidationError('A imagem deve ter sido enviada por esta conta administrativa.')
    return image


class CategoryAdminSerializer(serializers.ModelSerializer):
    image_attachment_key = serializers.SlugRelatedField(
        source='image', queryset=Image.objects.all(), slug_field='attachment_key',
        write_only=True, required=False, allow_null=True,
    )
    image = ImagePublicSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_attachment_key', 'sort_order', 'is_active']

    def validate_image_attachment_key(self, value):
        return validate_image_ownership(value, self.context)


class ProductAdminSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))
    promotional_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.00'), allow_null=True, required=False,
    )
    minimum_quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'description', 'ingredients', 'allergen_info',
            'conservation_info', 'price', 'promotional_price', 'unit',
            'minimum_quantity', 'minimum_lead_hours', 'is_active',
            'is_available', 'is_featured', 'sort_order',
        ]

    def validate(self, attrs):
        price = attrs.get('price', getattr(self.instance, 'price', None))
        promo = attrs.get('promotional_price', getattr(self.instance, 'promotional_price', None))
        if promo is not None and price is not None and promo > price:
            raise serializers.ValidationError({'promotional_price': 'Não pode superar o preço normal.'})
        return attrs


class ProductImageAdminSerializer(serializers.ModelSerializer):
    image_attachment_key = serializers.SlugRelatedField(
        source='image', queryset=Image.objects.all(), slug_field='attachment_key', write_only=True,
    )
    image = ImagePublicSerializer(read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'image_attachment_key', 'alt_text', 'sort_order']

    def validate_image_attachment_key(self, value):
        return validate_image_ownership(value, self.context)


class OptionGroupAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptionGroup
        fields = ['id', 'product', 'name', 'required', 'multiple', 'sort_order']


class OptionAdminSerializer(serializers.ModelSerializer):
    additional_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.00'))

    class Meta:
        model = ProductOption
        fields = ['id', 'group', 'name', 'additional_price', 'is_active', 'sort_order']


class ShopBrandPublicSerializer(serializers.ModelSerializer):
    logo = ImagePublicSerializer(read_only=True)

    class Meta:
        model = ShopBrand
        fields = ['name', 'logo', 'background_color', 'primary_color', 'heading_color']


class ShopBrandAdminSerializer(ShopBrandPublicSerializer):
    logo_attachment_key = serializers.SlugRelatedField(
        source='logo', queryset=Image.objects.all(), slug_field='attachment_key',
        write_only=True, required=False, allow_null=True,
    )

    class Meta(ShopBrandPublicSerializer.Meta):
        fields = [*ShopBrandPublicSerializer.Meta.fields, 'logo_attachment_key']

    def validate_logo_attachment_key(self, value):
        return validate_image_ownership(value, self.context)

    def validate(self, attrs):
        import re
        for key in ('background_color', 'primary_color', 'heading_color'):
            color = attrs.get(key)
            if color is not None and not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
                raise serializers.ValidationError({key: 'Utilize uma cor hexadecimal no formato #RRGGBB.'})
        return attrs
