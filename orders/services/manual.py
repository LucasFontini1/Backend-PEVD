import hashlib
import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from orders.models import DeliveryZone, Order, OrderItem, OrderItemOption, OrderStatusHistory
from orders.services.pricing import calculate_lines
from orders.services.scheduling import validate_window

CENTS = Decimal('0.01')


def manual_digest(payload):
    normalized = {
        'name': payload['customer_name'], 'phone': payload['customer_phone'],
        'email': payload['customer_email'], 'items': sorted([
            [item['product_id'], item['quantity'], sorted(item['selected_option_ids'])]
            for item in payload['items']
        ]), 'fulfillment': payload['fulfillment_type'],
        'scheduled': payload['scheduled_at'].isoformat(),
        'address': payload.get('address'), 'notes': payload['notes'],
    }
    return hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()


def get_delivery(payload, subtotal):
    if payload['fulfillment_type'] == 'pickup':
        return None, Decimal('0.00')
    address = payload['address']
    postal = address['zip_code']
    zone = next((
        zone for zone in DeliveryZone.objects.filter(is_active=True).order_by('-zip_prefix')
        if postal.startswith(zone.zip_prefix)
    ), None)
    if not zone:
        raise ValidationError({'address': 'CEP sem cobertura de entrega.'})
    if subtotal < zone.minimum_order:
        raise ValidationError({'items': 'Pedido abaixo do mínimo da zona de entrega.'})
    return dict(address), zone.fee


@transaction.atomic
def create_manual_order(actor, payload):
    key = payload['idempotency_key']
    digest = manual_digest(payload)
    existing = Order.objects.select_for_update().filter(
        source=Order.Source.WHATSAPP, idempotency_key=key,
    ).first()
    if existing:
        if existing.request_digest != digest:
            raise ValidationError({'idempotency_key': 'Esta chave já foi utilizada com outros dados.'})
        return existing, False

    lines, subtotal = calculate_lines(payload['items'])
    validate_window(payload['scheduled_at'], payload['fulfillment_type'], lines)
    address, shipping = get_delivery(payload, subtotal)
    user = None
    if payload['customer_email']:
        user = get_user_model().objects.filter(email__iexact=payload['customer_email']).first()
        if user and not user.is_active:
            user = None
    order = Order.objects.create(
        user=user, source=Order.Source.WHATSAPP,
        customer_name=payload['customer_name'], customer_phone=payload['customer_phone'],
        idempotency_key=key, request_digest=digest,
        fulfillment_type=payload['fulfillment_type'], scheduled_at=payload['scheduled_at'],
        address_snapshot=address, notes=payload['notes'],
        subtotal=subtotal, shipping=shipping, total=(subtotal + shipping).quantize(CENTS),
    )
    for line in lines:
        item = OrderItem.objects.create(
            order=order, product=line['product'], product_name_snapshot=line['product_name_snapshot'],
            unit_price=line['unit_price'], quantity=line['quantity'], subtotal=line['subtotal'],
        )
        OrderItemOption.objects.bulk_create([
            OrderItemOption(item=item, **option) for option in line['options']
        ])
    OrderStatusHistory.objects.create(
        order=order, actor=actor, new_status=order.status,
        reason='Pedido recebido pelo WhatsApp e registrado pela administração.',
    )
    return order, True
