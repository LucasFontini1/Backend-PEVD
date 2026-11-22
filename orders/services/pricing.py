from decimal import Decimal

from rest_framework.exceptions import ValidationError

from catalog.models import Product

CENTS = Decimal('0.01')


def calculate_lines(lines):
    ids = [line['product_id'] for line in lines]
    products = {
        product.id: product for product in Product.objects.filter(
            id__in=ids, is_active=True, is_available=True, category__is_active=True,
        ).prefetch_related('option_groups__options')
    }
    result = []
    subtotal = Decimal('0.00')
    for line in lines:
        product = products.get(line['product_id'])
        if not product:
            raise ValidationError({'items': 'Produto inexistente ou indisponível.'})
        quantity = line['quantity']
        if quantity < product.minimum_quantity:
            raise ValidationError({'items': f'Quantidade mínima para {product.name}: {product.minimum_quantity}.'})
        chosen = set(line['selected_option_ids'])
        all_options = {}
        selected = []
        for group in product.option_groups.all():
            options = {option.pk: option for option in group.options.all() if option.is_active}
            all_options.update(options)
            active_chosen = chosen.intersection(options)
            if group.required and not active_chosen:
                raise ValidationError({'items': f'Selecione {group.name} para {product.name}.'})
            if not group.multiple and len(active_chosen) > 1:
                raise ValidationError({'items': f'Selecione somente uma opção de {group.name}.'})
            for pk in sorted(active_chosen):
                option = options[pk]
                selected.append({
                    'group_name_snapshot': group.name, 'option_name_snapshot': option.name,
                    'additional_price_snapshot': option.additional_price,
                })
        if chosen.difference(all_options):
            raise ValidationError({'items': 'Opção indisponível ou não pertence ao produto.'})
        unit = product.effective_price + sum(
            (option['additional_price_snapshot'] for option in selected), Decimal('0.00'),
        )
        total_line = (unit * quantity).quantize(CENTS)
        result.append({
            'product': product, 'product_name_snapshot': product.name, 'quantity': quantity,
            'unit_price': unit.quantize(CENTS), 'subtotal': total_line, 'options': selected,
        })
        subtotal += total_line
    return result, subtotal.quantize(CENTS)
