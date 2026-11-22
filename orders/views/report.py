import csv
from datetime import date
from decimal import Decimal

from django.http import HttpResponse
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from orders.models import Order


def parse_dates(params):
    values = []
    for field in ('start', 'end'):
        value = params.get(field)
        try:
            values.append(date.fromisoformat(value) if value else None)
        except (ValueError, TypeError):
            raise ValidationError({field: 'Informe AAAA-MM-DD.'}) from None
    if values[0] and values[1] and values[0] > values[1]:
        raise ValidationError({'end': 'Data final menor que a inicial.'})
    return values


def completed_queryset(params):
    start, end = parse_dates(params)
    qs = Order.objects.filter(status=Order.Status.COMPLETED)
    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)
    return qs.order_by('created_at', 'pk')


def completed_report(request):
    qs = completed_queryset(request.query_params)
    paid = qs.filter(payment_status=Order.PaymentStatus.PAID)
    unpaid = qs.filter(payment_status=Order.PaymentStatus.PENDING)
    if request.query_params.get('download') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="pedidos-concluidos.csv"'
        response.write('\ufeff')
        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Codigo', 'Data', 'Origem', 'Cliente', 'Telefone', 'Pagamento',
            'Subtotal', 'Frete', 'Total',
        ])
        for order in qs.iterator():
            writer.writerow([
                str(order.public_id), order.created_at.isoformat(), order.source,
                order.customer_name, order.customer_phone, order.payment_status,
                order.subtotal, order.shipping, order.total,
            ])
        return response
    return Response({
        'orders_count': qs.count(), 'paid_count': paid.count(), 'unpaid_count': unpaid.count(),
        'paid_total': str((paid.aggregate(v=Sum('total'))['v'] or Decimal(0)).quantize(Decimal('0.01'))),
        'unpaid_total': str((unpaid.aggregate(v=Sum('total'))['v'] or Decimal(0)).quantize(Decimal('0.01'))),
        'results': [{
            'public_id': str(order.public_id), 'created_at': order.created_at,
            'source': order.source, 'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'payment_status': order.payment_status, 'total': str(order.total),
        } for order in qs[:500]],
    })
