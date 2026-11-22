from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class CommercialAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.normal = User.objects.create_user(
            email='normal@example.com', username='normal', password='Teste#2026aa',
        )
        self.staff = User.objects.create_user(
            email='staff@example.com', username='staff', password='Teste#2026aa', is_staff=True,
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com', username='admin', password='Teste#2026aa',
        )

    def test_anonymous_unauthorized(self):
        self.assertEqual(self.client.get('/api/admin/access/').status_code, 401)

    def test_staff_alone_is_forbidden(self):
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.get('/api/admin/access/').status_code, 403)

    def test_normal_user_forbidden(self):
        self.client.force_authenticate(user=self.normal)
        self.assertEqual(self.client.get('/api/admin/access/').status_code, 403)

    def test_active_superuser_allowed(self):
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.get('/api/admin/access/').status_code, 200)

    def test_inactive_superuser_forbidden(self):
        self.admin.is_active = False
        self.admin.save(update_fields=['is_active'])
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.get('/api/admin/access/').status_code, 403)
