from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from orders.models import BusinessHour, DeliveryZone

User = get_user_model()


class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='order-staff@example.com', username='order-staff',
            password='Senha#Orders2026', is_staff=True,
        )
        self.admin = User.objects.create_superuser(
            email='order-admin@example.com', username='order-admin', password='Senha#Orders2026',
        )

    def test_staff_cannot_configure_delivery(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.post('/api/admin/delivery-zones/', {
            'name': 'Centro', 'zip_prefix': '892', 'fee': '8.00',
        }, format='json').status_code, 403)

    def test_superuser_can_configure_hours_and_zone(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/admin/business-hours/', {
            'weekday': 1, 'opens_at': '09:00', 'closes_at': '17:00',
            'pickup_enabled': True, 'delivery_enabled': False,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        zone = self.client.post('/api/admin/delivery-zones/', {
            'name': 'Centro', 'zip_prefix': '892', 'fee': '8.00',
        }, format='json')
        self.assertEqual(zone.status_code, 201, zone.data)

    def test_zero_hours_means_no_purchases(self):
        self.assertEqual(BusinessHour.objects.count(), 0)
        self.assertEqual(DeliveryZone.objects.count(), 0)
