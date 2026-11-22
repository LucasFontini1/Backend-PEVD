from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from support.models import ContactInquiry, FAQ

User = get_user_model()


class FAQContactTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(email='faqstaff@example.com', username='faqstaff', password='Strong#2026', is_staff=True)
        self.admin = User.objects.create_superuser(email='faqadmin@example.com', username='faqadmin', password='Strong#2026')

    def test_public_faq_only_published(self):
        FAQ.objects.create(question='Publicado?', answer='Sim', published=True)
        FAQ.objects.create(question='Rascunho?', answer='Não', published=False)
        self.assertEqual(len(self.client.get('/api/faqs/').data['results']), 1)
        self.assertEqual(self.client.get('/api/faqs/2/').status_code, 404)

    def test_only_superuser_manages_faq(self):
        payload = {'question': 'Quando posso buscar?', 'answer': 'Horário a definir.', 'published': True}
        self.assertEqual(self.client.post('/api/admin/faqs/', payload).status_code, 401)
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.post('/api/admin/faqs/', payload).status_code, 403)
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.post('/api/admin/faqs/', payload).status_code, 201)

    def test_public_contact_and_honeypot(self):
        form = {'name': 'Ana', 'email': 'ana@example.com', 'subject': 'Minha dúvida',
                'message': 'Gostaria de saber se vocês atendem pelo site.', 'consent': True}
        self.assertEqual(self.client.post('/api/contact/', form, format='json').status_code, 202)
        self.assertEqual(ContactInquiry.objects.count(), 1)
        self.assertEqual(self.client.post('/api/contact/', {**form, 'website': 'https://spam.test'}, format='json').status_code, 202)
        self.assertEqual(ContactInquiry.objects.count(), 1)

    def test_contact_consent_and_message_required(self):
        body = {'name': 'Ana', 'email': 'ana@example.com', 'subject': 'Ajuda',
                'message': 'Preciso de orientação sobre encomenda.', 'consent': False}
        self.assertEqual(self.client.post('/api/contact/', body, format='json').status_code, 400)
        self.assertEqual(ContactInquiry.objects.count(), 0)
