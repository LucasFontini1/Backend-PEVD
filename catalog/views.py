from decimal import Decimal, InvalidOperation

from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from catalog.models import Category, Product, ProductImage, ProductOption, ProductOptionGroup
from catalog.serializers import (
    CategoryAdminSerializer, CategoryPublicSerializer, OptionAdminSerializer,
    OptionGroupAdminSerializer, ProductAdminSerializer, ProductImageAdminSerializer, ProductPublicSerializer,
)
from core.permissions import IsActiveSuperUser


class CategoryPublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CategoryPublicSerializer
    lookup_field = 'slug'
    queryset = Category.objects.filter(is_active=True).select_related('image')


class ProductPublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProductPublicSerializer
    lookup_field = 'slug'
    queryset = (
        Product.objects.filter(is_active=True, category__is_active=True)
        .select_related('category', 'category__image')
        .prefetch_related('images__image', 'option_groups__options')
    )

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('search'):
            qs = qs.filter(Q(name__icontains=p['search']) | Q(description__icontains=p['search']))
        if p.get('category'):
            qs = qs.filter(category__slug=p['category'])
        if p.get('available') == 'true':
            qs = qs.filter(is_available=True)
        if p.get('featured') == 'true':
            qs = qs.filter(is_featured=True)
        for key, lookup in [('min_price', 'gte'), ('max_price', 'lte')]:
            if key in p:
                try:
                    price = Decimal(p[key])
                    if not price.is_finite() or price < 0:
                        raise ValueError()
                except (InvalidOperation, ValueError):
                    raise ValidationError({key: 'Informe um preço decimal válido e não negativo.'}) from None
                qs = qs.filter(**{f'price__{lookup}': price})
        ordering = p.get('ordering', 'sort_order')
        allowed = {'sort_order', 'name', '-name', 'price', '-price'}
        if ordering not in allowed:
            raise ValidationError({'ordering': 'Ordenação não permitida.'})
        return qs.order_by(ordering, 'id')


class BaseAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveSuperUser]


class CategoryAdminViewSet(BaseAdminViewSet):
    serializer_class = CategoryAdminSerializer
    queryset = Category.objects.all().select_related('image')

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class ProductAdminViewSet(BaseAdminViewSet):
    serializer_class = ProductAdminSerializer
    queryset = Product.objects.all().select_related('category')

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class ProductImageAdminViewSet(BaseAdminViewSet):
    serializer_class = ProductImageAdminSerializer
    queryset = ProductImage.objects.all().select_related('product', 'image')


class OptionGroupAdminViewSet(BaseAdminViewSet):
    serializer_class = OptionGroupAdminSerializer
    queryset = ProductOptionGroup.objects.all().select_related('product')


class OptionAdminViewSet(BaseAdminViewSet):
    serializer_class = OptionAdminSerializer
    queryset = ProductOption.objects.all().select_related('group')
