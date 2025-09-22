from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib .auth import get_user_model
from stores.models import SellerRequest

User = get_user_model()

class SellerRequestTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email= 'seller@test.com', password='seller123')
        self.client.force_authenticate(user=self.user)

    def test_create_seller_request(self):
        url = reverse('seller_requests-list')
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SellerRequest.objects.count(),1)
        self.assertEqual(SellerRequest.objects.first().status, SellerRequest.PENDING)
    
    def test_duplicate_request_not_allowed(self):
        SellerRequest.objects.create(user=self.user, status=SellerRequest.PENDING)
        url = reverse('seller_requests-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pending', response.data['detail'])
