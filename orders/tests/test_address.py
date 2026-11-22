from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AddressTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.first = User.objects.create_user(email='a-address@example.com', username='a-address', password='Safe#2026One')
        self.second = User.objects.create_user(email='b-address@example.com', username='b-address', password='Safe#2026Two')
        self.payload = {
            'label': 'Casa', 'zip_code': '89225-000', 'street': 'Rua de teste',
            'number': '12', 'district': 'Bairro', 'city': 'Joinville', 'state': 'sc',
        }

    def test_owner_and_zipcode_validation(self):
        self.client.force_authenticate(user=self.first)
        result = self.client.post('/api/addresses/', self.payload, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data['zip_code'], '89225000')
        pk = result.data['id']
        self.client.force_authenticate(user=self.second)
        self.assertEqual(self.client.get(f'/api/addresses/{pk}/').status_code, 404)
        self.assertEqual(self.client.patch(f'/api/addresses/{pk}/', {'street': 'Invasor'}, format='json').status_code, 404)
        self.assertEqual(self.client.delete(f'/api/addresses/{pk}/').status_code, 404)

    def test_invalid_zipcode_fails(self):
        self.client.force_authenticate(user=self.first)
        invalid = {**self.payload, 'zip_code': 'abc'}
        self.assertEqual(self.client.post('/api/addresses/', invalid, format='json').status_code, 400)
