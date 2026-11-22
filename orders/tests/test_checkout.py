from datetime import timedelta, time
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product, ProductOption, ProductOptionGroup
from orders.models import BusinessHour, Order

User = get_user_model()


class CheckoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='client-orders@example.com', username='client-orders', password='Senha#Orders2026',
        )
        self.other = User.objects.create_user(
            email='other-orders@example.com', username='other-orders', password='Senha#Orders2026',
        )
        self.staff = User.objects.create_user(
            email='staff-orders@example.com', username='staff-orders',
            password='Senha#Orders2026', is_staff=True,
        )
        self.superuser = User.objects.create_superuser(
            email='super-orders@example.com', username='super-orders', password='Senha#Orders2026',
        )
        self.category = Category.objects.create(name='Teste pedido', slug='teste-pedido')
        self.product = Product.objects.create(
            category=self.category, name='Doce teste', slug='doce-teste',
            price=Decimal('12.30'), minimum_lead_hours=1,
        )
        self.group = ProductOptionGroup.objects.create(product=self.product, name='Tamanho', required=True)
        self.option = ProductOption.objects.create(group=self.group, name='Grande', additional_price='3.20')
        for weekday in range(7):
            BusinessHour.objects.create(
                weekday=weekday, opens_at=time(0, 0), closes_at=time(23, 59), pickup_enabled=True,
            )
        self.future = (timezone.now() + timedelta(days=4)).replace(hour=15, minute=0, second=0, microsecond=0)
        self.client.force_authenticate(user=self.user)

    def payload(self):
        return {
            'items': [{
                'product_id': self.product.pk, 'quantity': 2,
                'selected_option_ids': [self.option.pk],
            }],
            'fulfillment_type': 'pickup', 'scheduled_at': self.future.isoformat(),
            'notes': 'Sem embalagem especial',
        }

    def quote_and_order(self, payload=None):
        data = payload or self.payload()
        quote = self.client.post('/api/orders/quote/', data, format='json')
        self.assertEqual(quote.status_code, 200, quote.data)
        return self.client.post('/api/orders/', {
            **data, 'quote_hash': quote.data['quote_hash'],
            'idempotency_key': str(uuid4()),
        }, format='json')

    def test_price_calculated_server_side_with_snapshot(self):
        response = self.quote_and_order()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['total'], '31.00')
        self.assertEqual(response.data['payment_status'], 'pendente')
        self.assertEqual(response.data['status'], 'aguardando_confirmacao')
        self.product.price = Decimal('99.00')
        self.product.save(update_fields=['price'])
        detail = self.client.get('/api/orders/' + response.data['public_id'] + '/')
        self.assertEqual(detail.data['total'], '31.00')
        self.assertEqual(detail.data['items'][0]['product_name_snapshot'], 'Doce teste')
        self.assertEqual(len(detail.data['history']), 1)

    def test_anonymous_cannot_quote_or_order(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post('/api/orders/quote/', self.payload(), format='json').status_code, 401)
        self.assertEqual(self.client.post('/api/orders/', self.payload(), format='json').status_code, 401)

    def test_idor_other_user_not_found(self):
        response = self.quote_and_order()
        self.client.force_authenticate(user=self.other)
        self.assertEqual(self.client.get('/api/orders/' + response.data['public_id'] + '/').status_code, 404)
        self.assertEqual(len(self.client.get('/api/orders/').data['results']), 0)

    def test_retry_same_key_does_not_duplicate(self):
        data = self.payload()
        quote = self.client.post('/api/orders/quote/', data, format='json').data
        body = {**data, 'quote_hash': quote['quote_hash'], 'idempotency_key': str(uuid4())}
        first = self.client.post('/api/orders/', body, format='json')
        second = self.client.post('/api/orders/', body, format='json')
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(second.status_code, 200, second.data)
        self.assertEqual(Order.objects.count(), 1)

    def test_key_reused_with_another_order_rejected(self):
        data = self.payload()
        quote = self.client.post('/api/orders/quote/', data, format='json').data
        body = {**data, 'quote_hash': quote['quote_hash'], 'idempotency_key': str(uuid4())}
        self.assertEqual(self.client.post('/api/orders/', body, format='json').status_code, 201)
        changed = {**body, 'notes': 'Alterado'}
        self.assertEqual(self.client.post('/api/orders/', changed, format='json').status_code, 400)

    def test_forged_price_or_stale_quote_rejected(self):
        data = self.payload()
        quote = self.client.post('/api/orders/quote/', data, format='json').data
        self.product.price = Decimal('19.00')
        self.product.save(update_fields=['price'])
        body = {**data, 'total': '0.01', 'price': '0.01',
                'quote_hash': quote['quote_hash'], 'idempotency_key': str(uuid4())}
        self.assertEqual(self.client.post('/api/orders/', body, format='json').status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_unconfigured_delivery_is_rejected(self):
        data = {**self.payload(), 'fulfillment_type': 'delivery', 'address_id': 1}
        self.assertEqual(self.client.post('/api/orders/quote/', data, format='json').status_code, 400)

    def test_option_from_other_product_is_rejected(self):
        second = Product.objects.create(category=self.category, name='Outro doce', slug='outro-doce', price='2.00')
        group = ProductOptionGroup.objects.create(product=second, name='Teste')
        wrong_option = ProductOption.objects.create(group=group, name='Outro', additional_price='1.00')
        data = self.payload()
        data['items'][0]['selected_option_ids'] = [wrong_option.pk]
        self.assertEqual(self.client.post('/api/orders/quote/', data, format='json').status_code, 400)

    def test_cancelled_date_is_rejected(self):
        from orders.models import BlockedDate
        BlockedDate.objects.create(date=timezone.localtime(self.future).date())
        self.assertEqual(self.client.post('/api/orders/quote/', self.payload(), format='json').status_code, 400)
