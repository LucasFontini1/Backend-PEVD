from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class StoreSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            email='client@example.com', username='client', password='Teste#2026aa',
        )

    def test_login_returns_access_but_not_refresh(self):
        response = self.client.post('/api/token/', {
            'login': 'client', 'password': 'Teste#2026aa',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertTrue(response.cookies['pv_refresh']['httponly'])

    def test_refresh_requires_csrf(self):
        self.client.post('/api/token/', {
            'login': 'client', 'password': 'Teste#2026aa',
        }, format='json')
        self.assertEqual(self.client.post('/api/token/refresh/', {}, format='json').status_code, 403)

    def test_public_registration_cannot_set_privileges(self):
        response = self.client.post('/api/registro/', {
            'email': 'other@example.com', 'username': 'other', 'password': 'Teste#2026bb',
            'accepted_terms': True, 'is_superuser': True, 'is_staff': True,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        created = User.objects.get(username='other')
        self.assertFalse(created.is_staff)
        self.assertFalse(created.is_superuser)

    def test_terms_required(self):
        response = self.client.post('/api/registro/', {
            'email': 'other@example.com', 'username': 'other',
            'password': 'Teste#2026bb', 'accepted_terms': False,
        }, format='json')
        self.assertEqual(response.status_code, 400)
