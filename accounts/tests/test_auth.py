import pytest
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.email = 'firo744@example.com'
        self.password = '12345678Fh'
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_login_success(self):
        url = reverse('login-list')
        data = {'email': self.email, 'password': self.password}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        url = reverse('login-list')
        data = {'email': self.email, 'password': 'wrong-password'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        






