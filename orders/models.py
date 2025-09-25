from django.db import models
from core.models import BaseModel
from accounts.models import Address
from stores.models import StoreItem
from django.contrib.auth import get_user_model


User = get_user_model()

class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart_user')
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def total_price(self):
        subtotal = sum(item.total_price for item in self.cartitem_cart.all())
        return max(subtotal - self.total_discount, 0)

        
    def __str__(self):
        return f'Cart of {self.user.email}'

    
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitem_cart')
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='cartitem_storeitem')
    quantity = models.PositiveIntegerField(default=1)


    @property
    def total_price(self):
        price = self.store_item.discount_price if self.store_item.discount_price > 0 else self.store_item.price
        return self.quantity * price
    
    def __str__(self):
        return f'{self.store_item.product.name} x {self.quantity}'


class Order(BaseModel):
    PENDING = 1
    PROCESSING = 2
    DELIVERED = 3
    CANCELLED = 4
    FAILED = 5

    ORDER_STATUS = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (DELIVERED, "Delivered"),
        (CANCELLED, "Cancelled"),
        (FAILED, "Failed"),
    ]

    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='order_customer')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_address')
    status = models.PositiveIntegerField(choices=ORDER_STATUS, default=PENDING)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'Order #{self.id} - {self.customer.email}'


class OrderItem(BaseModel):
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitem_order')
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='orderitem_storeitem')

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.order.id} - {self.store_item.product.name}'


class Payment(BaseModel):
    PENDING = 0
    SUCCESS = 1
    FAILED = 2

    PAYMENT_STATUS = [(PENDING,'Pending'), (SUCCESS,'Success'), (FAILED,'Failed')]
    status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS, default=PENDING)
    transaction_id = models.CharField(max_length=20, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    reference_id = models.CharField(max_length=50, blank=True, null=True)
    card_pan = models.CharField(max_length=20, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_order')

    def __str__(self):
        return f'Payment for order #{self.order.id} - {self.get_status_display()}'