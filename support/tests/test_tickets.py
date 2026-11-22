from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from support.models import CommercialAudit, SupportMessage, SupportTicket

User = get_user_model()


class TicketTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.a = User.objects.create_user(email='ticket-a@example.com', username='ticket-a', password='Strong#2026')
        self.b = User.objects.create_user(email='ticket-b@example.com', username='ticket-b', password='Strong#2026')
        self.staff = User.objects.create_user(email='ticket-staff@example.com', username='ticket-staff', password='Strong#2026', is_staff=True)
        self.admin = User.objects.create_superuser(email='ticket-admin@example.com', username='ticket-admin', password='Strong#2026')

    def create_ticket(self):
        self.client.force_authenticate(user=self.a)
        result = self.client.post('/api/support/tickets/', {
            'subject': 'Dúvida do meu pedido', 'message': 'Gostaria de confirmar o procedimento.',
        }, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        return result.data['id']

    def test_client_admin_reply_client_sees_thread(self):
        pk = self.create_ticket()
        self.assertEqual(SupportMessage.objects.filter(ticket_id=pk).count(), 1)
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/admin/support/tickets/{pk}/reply/', {'message': 'Respondemos por aqui.'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['status'], 'respondido')
        self.assertEqual(CommercialAudit.objects.filter(action='support.reply').count(), 1)
        self.client.force_authenticate(user=self.a)
        detail = self.client.get(f'/api/support/tickets/{pk}/')
        self.assertEqual(len(detail.data['messages']), 2)
        self.assertEqual(detail.data['messages'][1]['body'], 'Respondemos por aqui.')
        reopened = self.client.post(f'/api/support/tickets/{pk}/messages/', {'message': 'Obrigado!'}, format='json')
        self.assertEqual(reopened.status_code, 200, reopened.data)
        self.assertEqual(reopened.data['status'], 'aberto')

    def test_idor_and_staff_cannot_reply(self):
        pk = self.create_ticket()
        self.client.force_authenticate(user=self.b)
        self.assertEqual(self.client.get(f'/api/support/tickets/{pk}/').status_code, 404)
        self.assertEqual(self.client.post(f'/api/support/tickets/{pk}/messages/', {'message': 'Invasão'}, format='json').status_code, 404)
        self.assertEqual(len(self.client.get('/api/support/tickets/').data['results']), 0)
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.post(f'/api/admin/support/tickets/{pk}/reply/', {'message': 'Resposta'}, format='json').status_code, 403)

    def test_closed_ticket_blocks_client_messages(self):
        pk = self.create_ticket()
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.post(f'/api/admin/support/tickets/{pk}/close/').status_code, 200)
        self.client.force_authenticate(user=self.a)
        self.assertEqual(self.client.post(f'/api/support/tickets/{pk}/messages/', {'message': 'Ainda aqui'}, format='json').status_code, 400)
        self.assertEqual(SupportTicket.objects.get(pk=pk).status, SupportTicket.Status.CLOSED)

    def test_public_cannot_read_tickets(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/support/tickets/').status_code, 401)
