from django.db import models
from core.models import BaseModel
from accounts.models import CustomUser
from products.models import Product


class Store(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_seller')

    def __str__(self):
        return self.name
    

class StoreItem(BaseModel):
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='storeitem_product')
    Store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='storeitem_store')

    def __str__(self):
        return f"{self.product.name} ({self.store.name})"




