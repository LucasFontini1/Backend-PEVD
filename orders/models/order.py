from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models import Q


class Order(models.Model):
    class Source(models.TextChoices):
        SITE = 'site', 'Site'
        WHATSAPP = 'whatsapp', 'WhatsApp'

    class Status(models.TextChoices):
        WAITING = 'aguardando_confirmacao', 'Aguardando confirmação'
        CONFIRMED = 'confirmado', 'Confirmado'
        PREPARING = 'em_preparo', 'Em preparo'
        READY = 'pronto', 'Pronto'
        COMPLETED = 'concluido', 'Concluído'
        REJECTED = 'rejeitado', 'Rejeitado'
        CANCELLED = 'cancelado', 'Cancelado'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pendente', 'Pendente'
        PAID = 'pago', 'Pago'

    class Fulfillment(models.TextChoices):
        PICKUP = 'pickup', 'Retirada'
        DELIVERY = 'delivery', 'Entrega'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders',
        null=True, blank=True,
    )
    source = models.CharField(max_length=16, choices=Source.choices, default=Source.SITE)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    idempotency_key = models.UUIDField()
    request_digest = models.CharField(max_length=64)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.WAITING)
    payment_status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    fulfillment_type = models.CharField(max_length=12, choices=Fulfillment.choices)
    scheduled_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    address_snapshot = models.JSONField(null=True, blank=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'idempotency_key'], name='unique_order_idempotency_per_user'),
            models.UniqueConstraint(fields=['idempotency_key'], condition=Q(source='whatsapp'), name='unique_manual_order_key'),
            models.CheckConstraint(condition=Q(total__gte=0), name='order_total_nonnegative'),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True)
    product_name_snapshot = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)


class OrderItemOption(models.Model):
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='options')
    option_name_snapshot = models.CharField(max_length=120)
    group_name_snapshot = models.CharField(max_length=120)
    additional_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    previous_status = models.CharField(max_length=32, blank=True)
    new_status = models.CharField(max_length=32)
    reason = models.CharField(max_length=250, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['changed_at', 'id']
