from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, Product, ProductOptionGroup
from uploader.models import Image

User = get_user_model()


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Categoria de teste', slug='categoria-teste')
        self.product = Product.objects.create(
            category=self.category, name='Produto de teste', slug='produto-teste',
            price=Decimal('15.90'), is_available=True,
        )
        self.user = User.objects.create_user(
            email='cliente-catalog@example.com', username='cliente-catalog', password='Senha#2026Teste',
        )
        self.staff = User.objects.create_user(
            email='staff-catalog@example.com', username='staff-catalog', password='Senha#2026Teste',
            is_staff=True,
        )
        self.admin = User.objects.create_superuser(
            email='admin-catalog@example.com', username='admin-catalog', password='Senha#2026Teste',
        )

    def test_catalog_is_public(self):
        result = self.client.get('/api/products/')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data['results']), 1)
        self.assertEqual(self.client.get('/api/categories/').status_code, 200)

    def test_inactive_products_and_categories_hidden(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])
        self.assertEqual(len(self.client.get('/api/products/').data['results']), 0)
        self.product.is_active = True
        self.product.save(update_fields=['is_active'])
        self.category.is_active = False
        self.category.save(update_fields=['is_active'])
        self.assertEqual(self.client.get('/api/products/produto-teste/').status_code, 404)

    def test_filters_and_ordering(self):
        self.assertEqual(len(self.client.get('/api/products/?search=produto').data['results']), 1)
        self.assertEqual(len(self.client.get('/api/products/?min_price=20.00').data['results']), 0)
        self.assertEqual(self.client.get('/api/products/?ordering=invalid').status_code, 400)
        self.assertEqual(self.client.get('/api/products/?max_price=bad').status_code, 400)

    def test_admin_requires_superuser_not_staff(self):
        self.assertEqual(self.client.post('/api/admin/categories/', {'name': 'X', 'slug': 'x'}).status_code, 401)
        for user in [self.user, self.staff]:
            self.client.force_authenticate(user=user)
            response = self.client.post('/api/admin/categories/', {'name': 'X', 'slug': 'x'}, format='json')
            self.assertEqual(response.status_code, 403)

    def test_admin_create_modify_and_soft_delete(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/admin/products/', {
            'name': 'Outro produto', 'slug': 'outro-produto', 'category': self.category.pk,
            'price': '22.50',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        pk = response.data['id']
        self.assertEqual(self.client.get('/api/products/outro-produto/').status_code, 200)
        updated = self.client.patch(f'/api/admin/products/{pk}/', {'price': '25.00'}, format='json')
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.delete(f'/api/admin/products/{pk}/').status_code, 204)
        self.assertEqual(self.client.get('/api/products/outro-produto/').status_code, 404)
        self.assertTrue(Product.objects.filter(pk=pk, is_active=False).exists())

    def test_invalid_promotion_rejected(self):
        self.client.force_authenticate(user=self.admin)
        result = self.client.patch(
            f'/api/admin/products/{self.product.pk}/', {'promotional_price': '100.00'}, format='json',
        )
        self.assertEqual(result.status_code, 400)

    def test_admin_image_and_options_reach_public_detail(self):
        self.client.force_authenticate(user=self.admin)
        image = Image.objects.create(owner=self.admin, file='images/test-public.png', description='Foto teste')
        uploaded = self.client.post('/api/admin/product-images/', {
            'product': self.product.pk, 'image_attachment_key': str(image.attachment_key),
            'alt_text': 'Imagem ilustrativa do teste',
        }, format='json')
        self.assertEqual(uploaded.status_code, 201, uploaded.data)
        group = self.client.post('/api/admin/option-groups/', {
            'product': self.product.pk, 'name': 'Tamanho', 'required': True,
        }, format='json')
        self.assertEqual(group.status_code, 201, group.data)
        option = self.client.post('/api/admin/options/', {
            'group': group.data['id'], 'name': 'Grande', 'additional_price': '4.50',
        }, format='json')
        self.assertEqual(option.status_code, 201, option.data)
        public = self.client.get('/api/products/produto-teste/')
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public.data['images'][0]['alt_text'], 'Imagem ilustrativa do teste')
        self.assertEqual(public.data['option_groups'][0]['options'][0]['additional_price'], '4.50')

    def test_cannot_associate_another_user_image(self):
        self.client.force_authenticate(user=self.admin)
        foreign = Image.objects.create(owner=self.user, file='images/not-owned.png')
        response = self.client.post('/api/admin/product-images/', {
            'product': self.product.pk, 'image_attachment_key': str(foreign.attachment_key),
            'alt_text': 'Não autorizado',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_option_price_cannot_be_negative(self):
        self.client.force_authenticate(user=self.admin)
        group = ProductOptionGroup.objects.create(product=self.product, name='Sabor')
        result = self.client.post('/api/admin/options/', {
            'group': group.pk, 'name': 'Teste', 'additional_price': '-1.00',
        }, format='json')
        self.assertEqual(result.status_code, 400)

    def test_staff_cannot_upload_to_catalog(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post('/api/admin/products/', {
            'name': 'Bloqueado', 'slug': 'bloqueado', 'category': self.category.pk,
            'price': '10.00',
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_price_filter_uses_promotional_price(self):
        self.product.promotional_price = Decimal('9.50')
        self.product.save(update_fields=['promotional_price'])
        response = self.client.get('/api/products/?max_price=10.00')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['effective_price'], '9.50')
