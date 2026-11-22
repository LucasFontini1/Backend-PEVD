import hashlib
import hmac
import json
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from orders.models import Order, OrderItem, OrderItemOption, OrderStatusHistory
from orders.services.pricing import calculate_lines
from orders.services.scheduling import validate_schedule


def request_digest(payload):
    normal = {
        'items': sorted([
            [line['product_id'], line['quantity'], sorted(line['selected_option_ids'])]
            for line in payload['items']
        ]),
        'fulfillment_type': payload['fulfillment_type'],
        'scheduled_at': payload['scheduled_at'].isoformat(),
        'address_id': payload.get('address_id'),
        'notes': payload['notes'],
    }
    return hashlib.sha256(json.dumps(normal, sort_keys=True).encode()).hexdigest()


def priced_quote(user, payload):
    items, subtotal = calculate_lines(payload['items'])
    address, fee = validate_schedule(
        user, payload['scheduled_at'], payload['fulfillment_type'],
        payload.get('address_id'), items, subtotal,
    )
    shipping = Decimal(str(fee)).quantize(Decimal('0.01'))
    total = subtotal + shipping
    compact = {
        'digest': request_digest(payload), 'subtotal': str(subtotal),
        'shipping': str(shipping), 'total': str(total),
        'lines': [
            [entry['product'].pk, str(entry['unit_price']), entry['quantity'],
             [[o['option_name_snapshot'], str(o['additional_price_snapshot'])] for o in entry['options']]]
            for entry in items
        ],
    }
    token = hmac.new(
        settings.SECRET_KEY.encode(),
        json.dumps(compact, sort_keys=True).encode(), hashlib.sha256,
    ).hexdigest()
    return {
        'items': items, 'address': address, 'shipping': shipping,
        'subtotal': subtotal, 'total': total, 'quote_hash': token,
    }


def public_quote(quote):
    return {
        'subtotal': str(quote['subtotal']), 'shipping': str(quote['shipping']),
        'total': str(quote['total']), 'quote_hash': quote['quote_hash'],
        'items': [
            {
                'product_id': item['product'].pk, 'name': item['product_name_snapshot'],
                'quantity': item['quantity'], 'unit_price': str(item['unit_price']),
                'subtotal': str(item['subtotal']),
            } for item in quote['items']
        ],
    }


def create_order(user, payload):
    key = payload.get('idempotency_key')
    if key is None:
        raise ValidationError({'idempotency_key': 'Chave de idempotência obrigatória.'})
    digest = request_digest(payload)
    existing = Order.objects.filter(user=user, idempotency_key=key).first()
    if existing:
        if existing.request_digest != digest:
            raise ValidationError({'idempotency_key': 'Chave já usada com outro pedido.'})
        return existing, False
    with transaction.atomic():
        quote = priced_quote(user, payload)
        if not hmac.compare_digest(quote['quote_hash'], payload.get('quote_hash', '')):
            raise ValidationError({'quote_hash': 'Valores mudaram. Revise o resumo antes de confirmar.'})
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=user, customer_name=(user.name or '').strip() or user.username,
                    idempotency_key=key, request_digest=digest,
                    fulfillment_type=payload['fulfillment_type'],
                    scheduled_at=payload['scheduled_at'], notes=payload['notes'],
                    address_snapshot=quote['address'], shipping=quote['shipping'],
                    subtotal=quote['subtotal'], total=quote['total'],
                )
                for line in quote['items']:
                    item = OrderItem.objects.create(
                        order=order, product=line['product'],
                        product_name_snapshot=line['product_name_snapshot'],
                        unit_price=line['unit_price'], quantity=line['quantity'], subtotal=line['subtotal'],
                    )
                    OrderItemOption.objects.bulk_create([
                        OrderItemOption(item=item, **option) for option in line['options']
                    ])
                OrderStatusHistory.objects.create(order=order, new_status=order.status, actor=user)
        except IntegrityError:
            order = Order.objects.get(user=user, idempotency_key=key)
            if order.request_digest != digest:
                raise ValidationError({'idempotency_key': 'Chave já usada com outro pedido.'}) from None
            return order, False
    return order, True
