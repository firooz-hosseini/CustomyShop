from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store, SellerRequest


User = get_user_model()


class StoreTests(APITestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(email="seller@example.com", password="pass123", role="seller")
        self.other_user = User.objects.create_user(email="other@example.com", password="pass123", role="seller")
        self.staff_user = User.objects.create_superuser(email="admin@example.com", password="admin123")

        SellerRequest.objects.create(user=self.seller_user, status=SellerRequest.APPROVED)

  
        self.client.force_authenticate(user=self.seller_user)


    def test_approved_seller_can_create_store(self):
        url = reverse("mystore-list")
        data = {"name": "My Store", "description": "Best store"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.filter(seller=self.seller_user).count(), 1)

    def test_cannot_create_more_than_one_store(self):
        Store.objects.create(name="Existing Store", seller=self.seller_user)
        url = reverse("mystore-list")
        data = {"name": "Another Store", "description": "Second"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
