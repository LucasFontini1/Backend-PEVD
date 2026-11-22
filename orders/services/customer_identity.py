"""Identidade do comprador usada somente em endpoints administrativos ou do próprio titular."""


def customer_display_name(order):
    manual_name = (order.customer_name or '').strip()
    if manual_name:
        return manual_name
    if order.user_id and order.user:
        return (order.user.name or '').strip() or order.user.username
    return 'Cliente não identificado'
