from datetime import time, timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product
from orders.models import BusinessHour, Order

User = get_user_model()


class OrderTrustBoundaryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='security-orders@example.com', username='security-orders', password='Senha#Security2026',
        )
        self.other = User.objects.create_user(
            email='other-security@example.com', username='other-security', password='Senha#Security2026',
        )
        category = Category.objects.create(name='Teste segurança', slug='teste-seguranca')
        self.product = Product.objects.create(
            category=category, name='Doce segurança', slug='doce-seguranca', price='11.90',
        )
        for weekday in range(7):
            BusinessHour.objects.create(weekday=weekday, opens_at=time(0, 0), closes_at=time(23, 59))
        self.client.force_authenticate(user=self.user)
        self.data = {
            'items': [{'product_id': self.product.pk, 'quantity': 2, 'selected_option_ids': []}],
            'fulfillment_type': 'pickup', 'scheduled_at': (timezone.now() + timedelta(days=3)).isoformat(),
            'notes': '',
        }

    def test_payload_cannot_overwrite_server_prices_owner_or_status(self):
        quote = self.client.post('/api/orders/quote/', self.data, format='json')
        self.assertEqual(quote.status_code, 200, quote.data)
        result = self.client.post('/api/orders/', {
            **self.data, 'quote_hash': quote.data['quote_hash'],
            'idempotency_key': str(uuid4()), 'total': '0.01', 'shipping': '-100',
            'payment_status': 'pago', 'status': 'concluido', 'user': self.other.pk,
        }, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data['total'], '23.80')
        self.assertEqual(result.data['payment_status'], 'pendente')
        self.assertEqual(result.data['status'], 'aguardando_confirmacao')
        self.assertEqual(Order.objects.get(public_id=result.data['public_id']).user_id, self.user.pk)

    def test_database_enforces_one_idempotency_key_per_customer(self):
        key = uuid4()
        common = {
            'idempotency_key': key, 'request_digest': 'a' * 64,
            'fulfillment_type': 'pickup', 'scheduled_at': timezone.now() + timedelta(days=3),
            'subtotal': Decimal('1.00'), 'total': Decimal('1.00'),
        }
        Order.objects.create(user=self.user, **common)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(user=self.user, **common)
        self.assertEqual(Order.objects.count(), 1)
