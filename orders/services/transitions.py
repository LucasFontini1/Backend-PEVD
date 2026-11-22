from django.db import transaction
from rest_framework.exceptions import ValidationError

from orders.models import Order, OrderStatusHistory

NEXT = {
    Order.Status.WAITING: {Order.Status.CONFIRMED, Order.Status.REJECTED, Order.Status.CANCELLED},
    Order.Status.CONFIRMED: {Order.Status.PREPARING, Order.Status.CANCELLED},
    Order.Status.PREPARING: {Order.Status.READY},
    Order.Status.READY: {Order.Status.COMPLETED},
}


@transaction.atomic
def transition_order(order_id, actor, new_status, reason):
    order = Order.objects.select_for_update().get(pk=order_id)
    if new_status not in NEXT.get(order.status, set()):
        raise ValidationError({'status': 'Transição de pedido não permitida.'})
    old_status = order.status
    order.status = new_status
    order.save(update_fields=['status'])
    OrderStatusHistory.objects.create(
        order=order, actor=actor, previous_status=old_status,
        new_status=new_status, reason=reason,
    )
    return order


@transaction.atomic
def confirm_manual_payment(order_id, actor, reason):
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status in (Order.Status.CANCELLED, Order.Status.REJECTED):
        raise ValidationError({'payment_status': 'Pedido encerrado não pode ser quitado.'})
    if order.payment_status == Order.PaymentStatus.PAID:
        raise ValidationError({'payment_status': 'Pagamento já confirmado.'})
    order.payment_status = Order.PaymentStatus.PAID
    order.save(update_fields=['payment_status'])
    OrderStatusHistory.objects.create(
        order=order, actor=actor, previous_status=order.status,
        new_status=order.status, reason=f'Pagamento manual confirmado: {reason}',
    )
    return order
