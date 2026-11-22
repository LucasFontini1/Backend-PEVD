import re
from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from orders.models import BlockedDate, BusinessHour, CustomerAddress, DeliveryZone


def validate_window(scheduled_at, fulfillment_type, products):
    if scheduled_at <= timezone.now():
        raise ValidationError({'scheduled_at': 'Escolha uma data futura.'})
    local = timezone.localtime(scheduled_at)
    if BlockedDate.objects.filter(date=local.date()).exists():
        raise ValidationError({'scheduled_at': 'A loja não atende nesta data.'})
    delivery = fulfillment_type == 'delivery'
    windows = BusinessHour.objects.filter(weekday=local.weekday(), **{
        'delivery_enabled' if delivery else 'pickup_enabled': True,
    })
    if not any(window.opens_at <= local.time().replace(tzinfo=None) < window.closes_at for window in windows):
        raise ValidationError({'scheduled_at': 'Horário não disponível para esta modalidade.'})
    lead_hours = max(product['product'].minimum_lead_hours for product in products)
    if scheduled_at < timezone.now() + timedelta(hours=lead_hours):
        raise ValidationError({'scheduled_at': f'É necessária antecedência de {lead_hours} horas.'})


def validate_schedule(user, scheduled_at, fulfillment_type, address_id, products, subtotal):
    validate_window(scheduled_at, fulfillment_type, products)
    if fulfillment_type != 'delivery':
        return None, 0
    address = CustomerAddress.objects.filter(pk=address_id, user=user).first()
    if not address:
        raise ValidationError({'address_id': 'Endereço não encontrado.'})
    zip_code = re.sub(r'\D', '', address.zip_code)
    zone = next((
        zone for zone in DeliveryZone.objects.filter(is_active=True).order_by('-zip_prefix')
        if zip_code.startswith(zone.zip_prefix)
    ), None)
    if zone and subtotal < zone.minimum_order:
        raise ValidationError({'items': 'Pedido abaixo do valor mínimo da região.'})
    snapshot = {
        'label': address.label, 'zip_code': address.zip_code, 'street': address.street,
        'number': address.number, 'complement': address.complement,
        'district': address.district, 'city': address.city, 'state': address.state,
    }
    return snapshot, zone.fee if zone else 0
