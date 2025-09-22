from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store, SellerRequest

User = get_user_model()

class StoreTets(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="seller@store.com", password="pass123", role="seller")
        self.client.force_authenticate(user=self.user)

    def test_create_store_without_approval_fails(self):
        url = reverse('mystore-list')
        data = {"name": "My Store", "description": "Cool shop"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 0)

    
    def test_create_store_after_approval(self):
        SellerRequest.objects.create(user=self.user, status=SellerRequest.APPROVED)
        url = reverse("mystore-list")
        data = {"name": "My Store", "description": "Cool shop"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Store.objects.count(), 1)