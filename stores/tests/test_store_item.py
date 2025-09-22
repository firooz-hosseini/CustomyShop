from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from stores.models import Store, StoreItem, SellerRequest
from products.models import Product, Category

User = get_user_model()

class StoreItemTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='seller@item.com', password='pass123', role='seller')
        self.client.force_authenticate(user=self.user)
        SellerRequest.objects.create(user=self.user, status=SellerRequest.APPROVED)
        self.store = Store.objects.create(name='My Store', seller=self.user)
        self.category = Category.objects.create(name= 'Category 1 ', description='desc')
        self.product = Product.objects.create(name='Product 1', description='desc', category_id=1)

    def test_add_item_to_store(self):
        url = reverse('mystore_items-list')
        data = {
            'store': self.store.id,
            'product': self.product.id,
            'stock': 5,
            'price': '10.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(StoreItem.objects.count(), 1)