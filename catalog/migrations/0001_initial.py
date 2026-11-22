from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [('uploader', '0003_video')]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(max_length=140, unique=True)),
                ('description', models.TextField(blank=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='uploader.image')),
            ],
            options={
                'ordering': ['sort_order', 'name'],
                'indexes': [models.Index(fields=['is_active', 'sort_order'], name='catalog_cat_active_order_idx')],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=180)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('ingredients', models.TextField(blank=True)),
                ('allergen_info', models.TextField(blank=True)),
                ('conservation_info', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('promotional_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('unit', models.CharField(default='unidade', max_length=80)),
                ('minimum_quantity', models.PositiveIntegerField(default=1)),
                ('minimum_lead_hours', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('is_available', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog.category')),
            ],
            options={
                'ordering': ['sort_order', 'name'],
                'indexes': [
                    models.Index(fields=['is_active', 'is_available'], name='catalog_product_active_idx'),
                    models.Index(fields=['is_featured', 'sort_order'], name='catalog_product_feature_idx'),
                ],
                'constraints': [
                    models.CheckConstraint(condition=Q(price__gte=0), name='catalog_price_nonnegative'),
                    models.CheckConstraint(condition=Q(promotional_price__isnull=True) | Q(promotional_price__gte=0), name='catalog_promo_nonnegative'),
                    models.CheckConstraint(condition=Q(minimum_quantity__gte=1), name='catalog_minimum_quantity'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('alt_text', models.CharField(max_length=220)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='uploader.image')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='catalog.product')),
            ],
            options={
                'ordering': ['sort_order', 'id'],
                'constraints': [models.UniqueConstraint(fields=['product', 'image'], name='catalog_unique_product_image')],
            },
        ),
        migrations.CreateModel(
            name='ProductOptionGroup',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120)),
                ('required', models.BooleanField(default=False)),
                ('multiple', models.BooleanField(default=False)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option_groups', to='catalog.product')),
            ],
            options={'ordering': ['sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='ProductOption',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=120)),
                ('additional_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='catalog.productoptiongroup')),
            ],
            options={
                'ordering': ['sort_order', 'id'],
                'constraints': [models.CheckConstraint(condition=Q(additional_price__gte=0), name='catalog_option_price_nonnegative')],
            },
        ),
    ]
