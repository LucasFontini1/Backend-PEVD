from datetime import date

from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsActiveSuperUser
from orders.models import Order, OrderItem
from support.models import ContactInquiry, CustomQuote, SupportTicket


def parse_range(query):
    values = []
    for key in ('start', 'end'):
        raw = query.get(key)
        if raw:
            try:
                value = date.fromisoformat(raw)
            except ValueError:
                raise ValidationError({key: 'Utilize AAAA-MM-DD.'}) from None
        else:
            value = None
        values.append(value)
    start, end = values
    if start and end and start > end:
        raise ValidationError({'end': 'Fim anterior ao início.'})
    return start, end


def apply_dates(qs, start, end, field='created_at'):
    if start:
        qs = qs.filter(**{f'{field}__date__gte': start})
    if end:
        qs = qs.filter(**{f'{field}__date__lte': end})
    return qs


class DashboardView(APIView):
    permission_classes = [IsActiveSuperUser]

    def get(self, request):
        start, end = parse_range(request.query_params)
        orders = apply_dates(Order.objects.all(), start, end)
        paid = orders.filter(
            payment_status=Order.PaymentStatus.PAID,
        ).exclude(status__in=[Order.Status.REJECTED, Order.Status.CANCELLED])
        lines = OrderItem.objects.filter(order__in=orders)
        top = list(lines.values('product_name_snapshot').annotate(
            quantity=Sum('quantity'),
        ).order_by('-quantity', 'product_name_snapshot')[:5])
        tickets = apply_dates(SupportTicket.objects.all(), start, end)
        contacts = apply_dates(ContactInquiry.objects.all(), start, end)
        quotes = apply_dates(CustomQuote.objects.all(), start, end)
        return Response({
            'period': {'start': str(start) if start else None, 'end': str(end) if end else None},
            'orders_count': orders.count(),
            'paid_orders_count': paid.count(),
            'recorded_paid_revenue': str(paid.aggregate(total=Sum('total'))['total'] or 0),
            'contacts_count': contacts.count(),
            'open_tickets_count': tickets.filter(status=SupportTicket.Status.OPEN).count(),
            'quotes_pending_count': quotes.filter(status=CustomQuote.Status.REQUESTED).count(),
            'top_products': top,
        })
