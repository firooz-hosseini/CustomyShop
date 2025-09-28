from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store, StoreItem
from products.models import Product, Category
from orders.models import Order, Payment
from accounts.models import Address
from unittest.mock import patch

User = get_user_model()


class PaymentTests(APITestCase):
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

        self.order = Order.objects.create(
        customer=self.user,
        address=self.address,
        total_price=200,
        status=Order.PENDING
        )

    def test_payment_creation_for_order(self):
        payment = Payment.objects.create(order=self.order, amount=self.order.total_price)
        self.assertEqual(payment.status, Payment.PENDING)
        self.assertEqual(payment.amount, self.order.total_price)


    @patch("orders.views.requests.post")
    def test_payment_verification_success(self, mock_post):
        mock_post.return_value.json.return_value = {
            "data": {"code": 100, "ref_id": "TESTREF"}
        }

        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            fee=0,  
            reference_id="TESTAUTH",
        )

        verify_url = reverse("payments-verify", kwargs={"pk": payment.id})
        response = self.client.get(verify_url, {"Status": "OK", "Authority": "TESTAUTH"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.SUCCESS)
        self.assertEqual(payment.transaction_id, "TESTREF")

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.PROCESSING)
        
    def test_payment_verification_failure(self):
        payment = Payment.objects.create(
                order=self.order,
                amount=self.order.total_price,
                reference_id="TESTAUTH" 
            )        

        verify_url = reverse("payments-verify", kwargs={"pk": payment.id})

        response = self.client.get(verify_url, {"Status": "NOK", "Authority": "TESTAUTH"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.FAILED)
