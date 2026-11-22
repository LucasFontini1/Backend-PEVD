from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import ShopBrand


class ShopBrandTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            email='staff-brand@example.com', username='staff-brand',
            password='Senha#2026Teste', is_staff=True,
        )
        self.admin = get_user_model().objects.create_superuser(
            email='admin-brand@example.com', username='admin-brand', password='Senha#2026Teste',
        )

    def test_public_brand_uses_default_when_not_saved(self):
        response = self.client.get('/api/shop/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Pensei em Você Doces')

    def test_only_superuser_can_change_brand(self):
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.patch('/api/admin/shop-settings/', {'name': 'Novo'}, format='json').status_code, 403)
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch('/api/admin/shop-settings/', {
            'name': 'Minha confeitaria', 'primary_color': '#AA2277',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(ShopBrand.objects.count(), 1)
        self.assertEqual(self.client.get('/api/shop/settings/').data['name'], 'Minha confeitaria')

    def test_invalid_color_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch('/api/admin/shop-settings/', {
            'primary_color': 'url(javascript:evil)',
        }, format='json')
        self.assertEqual(response.status_code, 400)
