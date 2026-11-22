import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True
    dependencies = [('catalog', '0002_shopbrand'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='BlockedDate', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('date', models.DateField(unique=True)),
            ('reason', models.CharField(max_length=180, blank=True)),
        ]),
        migrations.CreateModel(name='BusinessHour', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('weekday', models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(7)])),
            ('opens_at', models.TimeField()), ('closes_at', models.TimeField()),
            ('pickup_enabled', models.BooleanField(default=True)),
            ('delivery_enabled', models.BooleanField(default=False)),
        ], options={'ordering': ['weekday', 'opens_at'],
                    'constraints': [
                        models.CheckConstraint(condition=Q(closes_at__gt=models.F('opens_at')), name='valid_business_hour'),
                        models.UniqueConstraint(fields=['weekday', 'opens_at', 'closes_at'], name='unique_business_window'),
                    ]}),
        migrations.CreateModel(name='DeliveryZone', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('name', models.CharField(max_length=120)), ('zip_prefix', models.CharField(max_length=8, unique=True)),
            ('fee', models.DecimalField(decimal_places=2, max_digits=9)),
            ('minimum_order', models.DecimalField(decimal_places=2, max_digits=9, default=0)),
            ('is_active', models.BooleanField(default=True)),
        ], options={'ordering': ['name'],
                    'constraints': [
                        models.CheckConstraint(condition=Q(fee__gte=0), name='delivery_fee_nonnegative'),
                        models.CheckConstraint(condition=Q(minimum_order__gte=0), name='delivery_minimum_nonnegative'),
                    ]}),
        migrations.CreateModel(name='CustomerAddress', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('label', models.CharField(max_length=80, default='Principal')),
            ('zip_code', models.CharField(max_length=8)), ('street', models.CharField(max_length=180)),
            ('number', models.CharField(max_length=24)), ('complement', models.CharField(max_length=100, blank=True)),
            ('district', models.CharField(max_length=120)), ('city', models.CharField(max_length=120)),
            ('state', models.CharField(max_length=2)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE, related_name='customer_addresses')),
        ], options={'ordering': ['id']}),
        migrations.CreateModel(name='Order', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('public_id', models.UUIDField(unique=True, default=uuid.uuid4, editable=False)),
            ('idempotency_key', models.UUIDField()), ('request_digest', models.CharField(max_length=64)),
            ('status', models.CharField(max_length=32, default='aguardando_confirmacao', choices=[
                ('aguardando_confirmacao', 'Aguardando confirmação'), ('confirmado', 'Confirmado'),
                ('em_preparo', 'Em preparo'), ('pronto', 'Pronto'), ('concluido', 'Concluído'),
                ('rejeitado', 'Rejeitado'), ('cancelado', 'Cancelado')])),
            ('payment_status', models.CharField(max_length=16, default='pendente', choices=[('pendente', 'Pendente'), ('pago', 'Pago')])),
            ('fulfillment_type', models.CharField(max_length=12, choices=[('pickup', 'Retirada'), ('delivery', 'Entrega')])),
            ('scheduled_at', models.DateTimeField()), ('notes', models.TextField(blank=True)),
            ('address_snapshot', models.JSONField(null=True, blank=True)),
            ('shipping', models.DecimalField(max_digits=10, decimal_places=2, default=0)),
            ('subtotal', models.DecimalField(max_digits=10, decimal_places=2)),
            ('total', models.DecimalField(max_digits=10, decimal_places=2)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT, related_name='orders')),
        ], options={'ordering': ['-created_at'],
                    'constraints': [
                        models.UniqueConstraint(fields=['user', 'idempotency_key'], name='unique_order_idempotency_per_user'),
                        models.CheckConstraint(condition=Q(total__gte=0), name='order_total_nonnegative'),
                    ]}),
        migrations.CreateModel(name='OrderItem', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('product_name_snapshot', models.CharField(max_length=180)),
            ('unit_price', models.DecimalField(max_digits=10, decimal_places=2)),
            ('quantity', models.PositiveIntegerField()), ('subtotal', models.DecimalField(max_digits=10, decimal_places=2)),
            ('order', models.ForeignKey(to='orders.order', on_delete=django.db.models.deletion.CASCADE, related_name='items')),
            ('product', models.ForeignKey(to='catalog.product', null=True, on_delete=django.db.models.deletion.SET_NULL)),
        ]),
        migrations.CreateModel(name='OrderItemOption', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('option_name_snapshot', models.CharField(max_length=120)),
            ('group_name_snapshot', models.CharField(max_length=120)),
            ('additional_price_snapshot', models.DecimalField(max_digits=10, decimal_places=2)),
            ('item', models.ForeignKey(to='orders.orderitem', on_delete=django.db.models.deletion.CASCADE, related_name='options')),
        ]),
        migrations.CreateModel(name='OrderStatusHistory', fields=[
            ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ('previous_status', models.CharField(max_length=32, blank=True)),
            ('new_status', models.CharField(max_length=32)), ('reason', models.CharField(max_length=250, blank=True)),
            ('changed_at', models.DateTimeField(auto_now_add=True)),
            ('actor', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ('order', models.ForeignKey(to='orders.order', on_delete=django.db.models.deletion.CASCADE, related_name='history')),
        ], options={'ordering': ['changed_at', 'id']}),
    ]
