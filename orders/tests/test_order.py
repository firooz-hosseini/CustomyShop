from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category
from stores.models import Store, StoreItem
from orders.models import Order, CartItem
from accounts.models import Address

User = get_user_model()


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass123")
        self.seller = User.objects.create_user(email="seller@example.com", password="pass123", role="seller")
        self.store = Store.objects.create(name="Seller Store", seller=self.seller)
        self.category = Category.objects.create(name="Category", description="Desc")
        self.product = Product.objects.create(name="Product1", description="Desc", category=self.category)
        self.store_item = StoreItem.objects.create(store=self.store, product=self.product, price=100, discount_price=0, stock=5)

        self.address = Address.objects.create(
            user=self.user,
            city="City",
            address_line_1="Line 1",
            address_line_2="",
            state="State",
            country="Country",
            postal_code="0000",
            label="Home"
        )

        self.client.force_authenticate(user=self.user)

        add_url = reverse("mycart-add-to-cart")
        self.client.post(add_url, {"store_item_id": self.store_item.id, "quantity": 2}, format="json")

    def test_checkout_creates_order(self):
        url = reverse("orders-checkout")
        data = {"address_id": self.address.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.address, self.address)
        self.assertEqual(order.orderitem_order.count(), 1)
        self.assertEqual(order.total_price, 200)  # 2 x 100

    def test_checkout_with_empty_cart_fails(self):
        CartItem.objects.filter(cart__user=self.user).delete()

        url = reverse("orders-checkout")
        data = {"address_id": self.address.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_checkout_with_invalid_address_fails(self):
        url = reverse("orders-checkout")
        data = {"address_id": 999}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_id", response.data)
