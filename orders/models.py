from django.db import models
from core.models import BaseModel
from accounts.models import CustomUser, Address
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


class Order(BaseModel):
    ORDER_STATUS = [(1,'Pending'),(2,'Processing'),(3,'Delivered'),(4,'Cancelled'),(5,'Failed')]
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='order_customer')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_address')
    status = models.PositiveIntegerField(choices=ORDER_STATUS, default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'Order #{self.id} - {self.customer.email}'


class OrderItem(BaseModel):
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='item_order')
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='item_store_item')

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.order.id} - {self.store_item.product.name}'

