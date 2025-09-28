from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store
from accounts.models import Address
from products.models import Category, Product

User = get_user_model()


class StoreAddressTests(APITestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(email="seller@example.com", password="pass123", role="seller")
        self.other_user = User.objects.create_user(email="other@example.com", password="pass123", role="seller")


        self.store = Store.objects.create(name="My Store", seller=self.seller_user)
        self.category = Category.objects.create(name="Test Category", description="Category")
        self.product = Product.objects.create(name="Test Product", description="Test", category=self.category)

        self.client.force_authenticate(user=self.seller_user)

    def test_owner_can_add_store_address(self):
        url = reverse("mystore_address-list")
        data = {
            "store_id": self.store.id,
            "label": "Main Store",
            "address_line_1": "123 St",
            "city": "Tehran",
            "state": "Tehran",
            "country": "Iran",
            "postal_code": "12345"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.filter(store=self.store).count(), 1)

    def test_non_owner_cannot_add_address(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("mystore_address-list")
        data = {
            "store_id": self.store.id,
            "label": "Fake Store",
            "address_line_1": "Fake St",
            "city": "Shiraz",
            "state": "Fars",
            "country": "Iran",
            "postal_code": "99999"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
