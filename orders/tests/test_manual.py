from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product
from orders.models import BusinessHour, DeliveryZone, Order, OrderStatusHistory

User = get_user_model()


class ManualOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            email='manual-customer@example.com', username='manual-customer', password='Safe#2026',
        )
        self.staff = User.objects.create_user(
            email='manual-staff@example.com', username='manual-staff',
            password='Safe#2026', is_staff=True,
        )
        self.admin = User.objects.create_superuser(
            email='manual-admin@example.com', username='manual-admin', password='Safe#2026',
        )
        category = Category.objects.create(name='Doces', slug='doces-manuais')
        self.product = Product.objects.create(
            category=category, name='Brigadeiro', slug='brigadeiro-manual',
            price=Decimal('5.00'), is_active=True, is_available=True,
        )
        for weekday in range(7):
            BusinessHour.objects.create(
                weekday=weekday, opens_at='09:00', closes_at='18:00',
                pickup_enabled=True, delivery_enabled=True,
            )
        scheduled = timezone.localtime(timezone.now() + timedelta(days=3)).replace(
            hour=12, minute=0, second=0, microsecond=0,
        )
        self.data = {
            'customer_name': 'Cliente WhatsApp',
            'customer_phone': '(47) 99999-0000',
            'items': [{'product_id': self.product.pk, 'quantity': 2, 'selected_option_ids': []}],
            'fulfillment_type': 'pickup', 'scheduled_at': scheduled.isoformat(),
            'idempotency_key': str(uuid4()),
        }

    def test_permissions_and_price_from_server(self):
        for user, expected in [(None, 401), (self.customer, 403), (self.staff, 403)]:
            self.client.force_authenticate(user=user)
            response = self.client.post('/api/admin/orders/manual/', self.data, format='json')
            self.assertEqual(response.status_code, expected, response.data)
        self.client.force_authenticate(user=self.admin)
        result = self.client.post('/api/admin/orders/manual/', {
            **self.data, 'total': '0.01', 'payment_status': 'pago', 'status': 'concluido',
        }, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        order = Order.objects.get()
        self.assertIsNone(order.user_id)
        self.assertEqual(order.source, Order.Source.WHATSAPP)
        self.assertEqual(order.total, Decimal('10.00'))
        self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
        self.assertEqual(order.status, Order.Status.WAITING)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(OrderStatusHistory.objects.filter(order=order, actor=self.admin).count(), 1)
        self.assertEqual(self.client.post('/api/admin/orders/manual/', self.data, format='json').status_code, 200)
        self.assertEqual(Order.objects.count(), 1)

    def test_cannot_reuse_idempotency_with_different_payload(self):
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.post('/api/admin/orders/manual/', self.data, format='json').status_code, 201)
        forged = {**self.data, 'customer_phone': '47988887777'}
        self.assertEqual(self.client.post('/api/admin/orders/manual/', forged, format='json').status_code, 400)
        self.assertEqual(Order.objects.count(), 1)

    def test_delivery_uses_zone_and_address(self):
        DeliveryZone.objects.create(
            name='Teste', zip_prefix='892', fee=Decimal('9.00'), minimum_order=Decimal('10.00'),
        )
        body = {**self.data, 'fulfillment_type': 'delivery', 'address': {
            'label': 'Casa', 'zip_code': '89225450', 'street': 'Rua Teste', 'number': '10',
            'district': 'Centro', 'city': 'Joinville', 'state': 'SC',
        }}
        self.client.force_authenticate(user=self.admin)
        result = self.client.post('/api/admin/orders/manual/', body, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        order = Order.objects.get()
        self.assertEqual(order.shipping, Decimal('9.00'))
        self.assertEqual(order.total, Decimal('19.00'))
        self.assertEqual(order.address_snapshot['zip_code'], '89225450')

    def test_missing_delivery_address_or_product_rejected(self):
        self.client.force_authenticate(user=self.admin)
        data = {**self.data, 'fulfillment_type': 'delivery'}
        self.assertEqual(self.client.post('/api/admin/orders/manual/', data, format='json').status_code, 400)
        bad = {**self.data, 'items': [{'product_id': 9999999, 'quantity': 1}]}
        self.assertEqual(self.client.post('/api/admin/orders/manual/', bad, format='json').status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
