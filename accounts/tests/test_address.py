from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Address

User = get_user_model()


class AddressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='addr@test.com', password='pass123')
        self.client.force_authenticate(user=self.user)

    def test_create_address_and_set_default(self):
        url = reverse('user_address-list')
        data = {
            'label': 'Home',
            'address_line_1': '123 Street',
            'city': 'MyCity',
            'state': 'MyState',
            'country': 'MyCountry',
            'postal_code': '12345',
            'is_default': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 1)
        self.assertTrue(Address.objects.first().is_default)