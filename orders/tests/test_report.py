from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from orders.models import Order

User = get_user_model()


class CompletedReportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            email='report-staff@example.com', username='report-staff',
            password='Safe#2026', is_staff=True,
        )
        self.admin = User.objects.create_superuser(
            email='report-admin@example.com', username='report-admin', password='Safe#2026',
        )
        for state, paid, amount in [
            (Order.Status.COMPLETED, Order.PaymentStatus.PAID, '50.00'),
            (Order.Status.COMPLETED, Order.PaymentStatus.PENDING, '30.00'),
            (Order.Status.CONFIRMED, Order.PaymentStatus.PAID, '90.00'),
        ]:
            Order.objects.create(
                source=Order.Source.WHATSAPP, customer_name='Pessoa Exemplo',
                customer_phone='47999990000', idempotency_key=uuid4(), request_digest='x' * 64,
                scheduled_at=timezone.now() + timedelta(days=1),
                fulfillment_type=Order.Fulfillment.PICKUP, subtotal=amount,
                total=amount, status=state, payment_status=paid,
            )

    def test_only_admin_and_totals(self):
        self.assertEqual(self.client.get('/api/admin/orders/completed-report/').status_code, 401)
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.get('/api/admin/orders/completed-report/').status_code, 403)
        self.client.force_authenticate(user=self.admin)
        result = self.client.get('/api/admin/orders/completed-report/')
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(result.data['orders_count'], 2)
        self.assertEqual(result.data['paid_total'], '50.00')
        self.assertEqual(result.data['unpaid_total'], '30.00')

    def test_csv_export_and_period(self):
        self.client.force_authenticate(user=self.admin)
        csv_response = self.client.get('/api/admin/orders/completed-report/?download=csv')
        self.assertEqual(csv_response.status_code, 200)
        self.assertIn('text/csv', csv_response['Content-Type'])
        self.assertIn('Pessoa Exemplo', csv_response.content.decode('utf-8-sig'))
        self.assertEqual(self.client.get('/api/admin/orders/completed-report/?start=xxx').status_code, 400)
        self.assertEqual(self.client.get('/api/admin/orders/completed-report/?start=2030-01-01').data['orders_count'], 0)
