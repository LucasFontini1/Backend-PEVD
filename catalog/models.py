from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    image = models.ForeignKey('uploader.Image', null=True, blank=True, on_delete=models.SET_NULL)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        indexes = [models.Index(fields=['is_active', 'sort_order'], name='catalog_cat_active_order_idx')]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    allergen_info = models.TextField(blank=True)
    conservation_info = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=80, default='unidade')
    minimum_quantity = models.PositiveIntegerField(default=1)
    minimum_lead_hours = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_available'], name='catalog_product_active_idx'),
            models.Index(fields=['is_featured', 'sort_order'], name='catalog_product_feature_idx'),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(price__gte=0), name='catalog_price_nonnegative'),
            models.CheckConstraint(
                condition=Q(promotional_price__isnull=True) | Q(promotional_price__gte=0),
                name='catalog_promo_nonnegative',
            ),
            models.CheckConstraint(condition=Q(minimum_quantity__gte=1), name='catalog_minimum_quantity'),
        ]

    def clean(self):
        if self.promotional_price is not None and self.promotional_price > self.price:
            raise ValidationError({'promotional_price': 'O preço promocional não pode superar o preço normal.'})

    @property
    def effective_price(self):
        return self.promotional_price if self.promotional_price is not None else self.price

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('uploader.Image', on_delete=models.PROTECT)
    alt_text = models.CharField(max_length=220)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        constraints = [models.UniqueConstraint(fields=['product', 'image'], name='catalog_unique_product_image')]


class ProductOptionGroup(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='option_groups')
    name = models.CharField(max_length=120)
    required = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']


class ProductOption(models.Model):
    group = models.ForeignKey(ProductOptionGroup, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=120)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        constraints = [
            models.CheckConstraint(condition=Q(additional_price__gte=0), name='catalog_option_price_nonnegative'),
        ]
