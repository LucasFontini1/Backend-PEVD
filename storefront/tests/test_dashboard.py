from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from orders.models import Order
from support.models import ContactInquiry, SupportTicket

User = get_user_model()


class DashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='dash-user@example.com', username='dash-user', password='Strong#2026')
        self.staff = User.objects.create_user(email='dash-staff@example.com', username='dash-staff', password='Strong#2026', is_staff=True)
        self.admin = User.objects.create_superuser(email='dash-admin@example.com', username='dash-admin', password='Strong#2026')

    def test_empty_dashboard_uses_true_zeros_and_requires_superuser(self):
        self.assertEqual(self.client.get('/api/admin/dashboard/').status_code, 401)
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.get('/api/admin/dashboard/').status_code, 403)
        self.client.force_authenticate(user=self.admin)
        data = self.client.get('/api/admin/dashboard/').data
        self.assertEqual(data['orders_count'], 0)
        self.assertEqual(data['recorded_paid_revenue'], '0.00')
        self.assertEqual(data['contacts_count'], 0)

    def test_only_marked_paid_orders_count_as_recorded_revenue(self):
        common = {
            'user': self.customer, 'idempotency_key': uuid4(),
            'request_digest': 'a' * 64, 'fulfillment_type': 'pickup',
            'scheduled_at': timezone.now(), 'subtotal': Decimal('30.00'), 'total': Decimal('30.00'),
        }
        Order.objects.create(**common, payment_status=Order.PaymentStatus.PAID, status=Order.Status.CONFIRMED)
        Order.objects.create(**{**common, 'idempotency_key': uuid4()}, payment_status=Order.PaymentStatus.PENDING)
        Order.objects.create(**{**common, 'idempotency_key': uuid4()}, payment_status=Order.PaymentStatus.PAID, status=Order.Status.CANCELLED)
        ContactInquiry.objects.create(name='Ana', email='ana@example.com', subject='Dúvida', message='Gostaria de atendimento.')
        SupportTicket.objects.create(user=self.customer, subject='Pergunta')
        self.client.force_authenticate(user=self.admin)
        result = self.client.get('/api/admin/dashboard/?start=2020-01-01')
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(result.data['orders_count'], 3)
        self.assertEqual(result.data['recorded_paid_revenue'], '30.00')
        self.assertEqual(result.data['contacts_count'], 1)
        self.assertEqual(result.data['open_tickets_count'], 1)
        self.assertEqual(self.client.get('/api/admin/dashboard/?start=not-a-date').status_code, 400)
