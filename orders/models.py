from django.db import models
from core.models import BaseModel
from accounts.models import CustomUser
from stores.models import StoreItem

class Cart(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_user')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'Cart of {self.user.email}'

    
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='item_cart')
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='item_store_item')
    quantity = models.PositiveIntegerField()


    def __str__(self):
        return f'{self.store_item.product.name} x {self.quantity}'

