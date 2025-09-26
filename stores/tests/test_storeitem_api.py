from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store, StoreItem
from products.models import Product, Category

User = get_user_model()


class StoreItemTests(APITestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(email="seller@example.com", password="pass123", role="seller")
        self.other_user = User.objects.create_user(email="other@example.com", password="pass123", role="seller")

        self.store = Store.objects.create(name="Owner Store", seller=self.seller_user)
        self.category = Category.objects.create(name="Test Category", description="Category")
        self.product = Product.objects.create(name="Test Product", description="Test", category=self.category)

        self.client.force_authenticate(user=self.seller_user)

    def test_storeitem_can_only_be_created_by_owner(self):
        url = reverse("mystore_items-list")
        data = {
            "store": self.store.id,
            "product": self.product.id,
            "price": 100,
            "discount_price": 50,
            "stock": 10
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_owner_cannot_update_delete_storeitem(self):
        item = StoreItem.objects.create(store=self.store, product=self.product, price=100, discount_price=50, stock=10)
        self.client.force_authenticate(user=self.other_user)
        url = reverse("mystore_items-detail", kwargs={"pk": item.id})

        response = self.client.patch(url, {"price": 200}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
