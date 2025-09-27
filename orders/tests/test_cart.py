from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category
from stores.models import Store, StoreItem
from orders.models import Cart

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass123")
        self.store_owner = User.objects.create_user(email="seller@example.com", password="pass123", role="seller")
        self.store = Store.objects.create(name="Owner Store", seller=self.store_owner)
        self.category = Category.objects.create(name="Category", description="Desc")
        self.product = Product.objects.create(name="Product1", description="Desc", category=self.category)
        self.store_item = StoreItem.objects.create(store=self.store, product=self.product, price=100, discount_price=0, stock=5)
        self.client.force_authenticate(user=self.user)

    def test_add_item_to_cart(self):
        url = reverse("mycart-add-to-cart")
        data = {"store_item_id": self.store_item.id, "quantity": 2}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["items"][0]["quantity"], 2)
        self.assertEqual(response.data["items"][0]["store_item_id"], self.store_item.id)

    def test_update_cart_item_quantity(self):
        add_url = reverse("mycart-add-to-cart")
        data = {"store_item_id": self.store_item.id, "quantity": 2}
        response = self.client.post(add_url, data, format="json")

        cart = Cart.objects.get(user=self.user)
        cart_item_id = cart.cartitem_cart.first().id

        url = reverse("mycart-update-quantity")
        data = {"cart_item_id": cart_item_id, "quantity": 3}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"][0]["quantity"], 3)


    def test_remove_item_from_cart(self):
        item1 = StoreItem.objects.create(store=self.store, product=self.product, price=100, stock=5)
        item2 = StoreItem.objects.create(store=self.store, product=self.product, price=100, stock=5)
        
        add_url = reverse("mycart-add-to-cart")
        self.client.post(add_url, {"store_item_id": item1.id, "quantity": 1}, format="json")
        self.client.post(add_url, {"store_item_id": item2.id, "quantity": 1}, format="json")

        cart = Cart.objects.get(user=self.user)
        cart_item = cart.cartitem_cart.first()

        remove_url = reverse("mycart-remove-item", kwargs={"pk": cart_item.id})
        response = self.client.delete(remove_url)
        self.assertEqual(response.status_code, 200)

        retrieve_url = reverse("mycart-detail", kwargs={"pk": cart_item.id})
        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, 404)

        list_url = reverse("mycart-list")
        response = self.client.get(list_url)
        self.assertEqual(len(response.data["items"]), 1)

    def test_add_more_than_stock(self):
        url = reverse("mycart-add-to-cart")
        data = {"store_item_id": self.store_item.id, "quantity": 10}  # stock is only 5
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data) 
        self.assertEqual(response.data["message"], "Only 5 items available in stock.")

    def test_decrease_quantity_to_zero_removes_item(self):
        add_url = reverse("mycart-add-to-cart")
        response = self.client.post(add_url, {"store_item_id": self.store_item.id, "quantity": 2}, format="json")

        cart = Cart.objects.get(user=self.user)
        cart_item_id = cart.cartitem_cart.first().id

        update_url = reverse("mycart-update-quantity")
        response = self.client.patch(update_url, {"cart_item_id": cart_item_id, "quantity": 0}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 0)