import pytest
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch

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
        

    @patch('accounts.services.send_otp_email_task.delay')
    def test_request_otp_sends_email(self, mock_send):
        url = reverse("request_otp-list") 
        data = {
            "email": "otp@example.com",
            "password": "pass1234"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_send.called)  


    @patch("accounts.services.send_otp_email_task.delay")
    def test_verify_otp_creates_user(self, mock_send):
        request_url = reverse("request_otp-list")
        data = {"email": "verify@example.com", "password": "pass1234"}
        self.client.post(request_url, data, format="json")

        from django.core.cache import cache
        cached = cache.get("otp_verify@example.com") or {}
        otp_code = cached.get("otp_code", "123456")

        verify_url = reverse("verify_otp-list")
        response = self.client.post(verify_url, {"email": "verify@example.com", "otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(mock_send.called) 




