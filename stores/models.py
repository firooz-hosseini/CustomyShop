from django.db import models
from core.models import BaseModel
from accounts.models import CustomUser ,Address
from products.models import Product

class Store(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='store_address')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_seller')


class StoreItem(BaseModel):
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='item_product')
    Store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='item_store')
    




