from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)

