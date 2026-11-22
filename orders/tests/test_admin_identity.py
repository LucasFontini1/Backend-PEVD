from types import SimpleNamespace

from django.test import SimpleTestCase
from django.urls import resolve

from app import settings
from orders.serializers.order import AdminOrderSerializer, OrderSerializer


class ProductionSecurityRegressionTests(SimpleTestCase):
    def test_django_admin_uses_configured_path(self):
        if settings.DJANGO_ADMIN_PATH:
            match = resolve(f'/{settings.DJANGO_ADMIN_PATH}/')
            self.assertEqual(match.app_name, 'admin')

    def test_customer_display_name_only_exists_in_admin_serializer(self):
        self.assertIn('customer_display_name', AdminOrderSerializer.Meta.fields)
        self.assertNotIn('customer_display_name', OrderSerializer.Meta.fields)

    def test_administrator_sees_registered_customer_name(self):
        order = SimpleNamespace(
            customer_name='',
            user_id=3,
            user=SimpleNamespace(name='Cliente Real', username='cliente123'),
        )
        self.assertEqual(
            AdminOrderSerializer().get_customer_display_name(order), 'Cliente Real',
        )

    def test_manual_order_uses_snapshot_name(self):
        order = SimpleNamespace(customer_name='Cliente do WhatsApp', user_id=None, user=None)
        self.assertEqual(
            AdminOrderSerializer().get_customer_display_name(order), 'Cliente do WhatsApp',
        )
