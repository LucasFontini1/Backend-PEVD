from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from orders.models import Order
from support.models import CommercialAudit, CustomQuote

User = get_user_model()


class QuoteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='quotes-a@example.com', username='quotes-a', password='Strong#2026')
        self.other = User.objects.create_user(email='quotes-b@example.com', username='quotes-b', password='Strong#2026')
        self.admin = User.objects.create_superuser(email='quotes-admin@example.com', username='quotes-admin', password='Strong#2026')

    def request_quote(self):
        self.client.force_authenticate(user=self.user)
        result = self.client.post('/api/quotes/', {
            'title': 'Bolo aniversário', 'details': 'Quero cobertura especial e recheio de chocolate.',
            'flavor': 'Chocolate', 'portions': 15,
            'desired_date': (timezone.localdate() + timedelta(days=10)).isoformat(),
            'proposed_price': '0.01', 'status': 'aceito',
        }, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data['status'], 'solicitado')
        self.assertIsNone(result.data['proposed_price'])
        return result.data['id']

    def test_proposal_price_and_accept_only_by_owner(self):
        pk = self.request_quote()
        self.client.force_authenticate(user=self.admin)
        proposal = self.client.post(f'/api/admin/quotes/{pk}/propose/', {
            'proposed_price': '245.50', 'proposed_details': 'Bolo a retirar na data combinada.',
            'valid_until': (timezone.now() + timedelta(days=5)).isoformat(),
        }, format='json')
        self.assertEqual(proposal.status_code, 200, proposal.data)
        self.client.force_authenticate(user=self.other)
        self.assertEqual(self.client.post(f'/api/quotes/{pk}/accept/').status_code, 404)
        self.client.force_authenticate(user=self.user)
        accepted = self.client.post(f'/api/quotes/{pk}/accept/')
        self.assertEqual(accepted.status_code, 200, accepted.data)
        self.assertEqual(accepted.data['status'], 'aceito')
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(CommercialAudit.objects.filter(action='quote.accept').count(), 1)

    def test_expired_quote_cannot_be_accepted(self):
        pk = self.request_quote()
        CustomQuote.objects.filter(pk=pk).update(
            status=CustomQuote.Status.PROPOSED, proposed_price='90.00',
            valid_until=timezone.now() - timedelta(minutes=1),
        )
        self.assertEqual(self.client.post(f'/api/quotes/{pk}/accept/').status_code, 400)
