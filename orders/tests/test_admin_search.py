from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, Product

User = get_user_model()


class AdminSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_superuser(
            email='catalog-search-admin@example.com', username='catalog-search-admin',
            password='Strong#2026',
        )
        self.staff = User.objects.create_user(
            email='catalog-search-staff@example.com', username='catalog-search-staff',
            password='Strong#2026', is_staff=True,
        )
        self.category = Category.objects.create(name='Bolos Decorados', slug='bolos-decorados')
        Category.objects.create(name='Brigadeiros', slug='brigadeiros-search')
        Product.objects.create(
            name='Bolo de Chocolate', slug='bolo-chocolate-search',
            category=self.category, price='50.00',
        )
        Product.objects.create(
            name='Bolo de Morango', slug='bolo-morango-search',
            category=self.category, price='60.00',
        )

    def test_search_restricted_to_admin(self):
        self.assertEqual(self.client.get('/api/admin/products/?search=bolo').status_code, 401)
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.get('/api/admin/categories/?search=bolos').status_code, 403)

    def test_name_search_server_side(self):
        self.client.force_authenticate(user=self.owner)
        result = self.client.get('/api/admin/products/?search=chocolate')
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(len(result.data['results']), 1)
        self.assertEqual(result.data['results'][0]['name'], 'Bolo de Chocolate')
        categories = self.client.get('/api/admin/categories/?search=decorados')
        self.assertEqual(len(categories.data['results']), 1)
