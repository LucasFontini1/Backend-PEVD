from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from storefront.models import Banner

User = get_user_model()


class BannerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='banner-user@example.com', username='banner-user', password='Strong#2026')
        self.admin = User.objects.create_superuser(email='banner-admin@example.com', username='banner-admin', password='Strong#2026')

    def test_only_active_banners_public(self):
        Banner.objects.create(title='Aberto', link_path='/cardapio', is_active=True)
        Banner.objects.create(title='Não publicado', link_path='/cardapio', is_active=False)
        self.assertEqual(len(self.client.get('/api/banners/').data['results']), 1)

    def test_admin_only_and_safe_internal_links(self):
        payload = {'title': 'Veja o cardápio', 'link_path': '//evil.example', 'is_active': True}
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.post('/api/admin/banners/', payload).status_code, 403)
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.post('/api/admin/banners/', payload).status_code, 400)
        payload['link_path'] = '/cardapio'
        self.assertEqual(self.client.post('/api/admin/banners/', payload).status_code, 201)
