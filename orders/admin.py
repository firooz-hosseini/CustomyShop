from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('id', 'store_item', 'quantity', 'total_price')
    readonly_fields = ('total_price',)
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'total_discount')
    search_fields = ('id', 'user__email',)
    readonly_fields = ('total_price',)
    ordering = ('-id', '-created_at',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'store_item', 'quantity', 'total_price')
    search_fields = ('id', 'cart__user__email', 'store_item__product__name')
    ordering = ('-id', '-created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('id', 'store_item', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_price', 'total_discount')
    list_filter = ('id', 'status',)
    search_fields = ('id', 'customer__email', 'address__street')
    ordering = ('-id', '-created_at',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'store_item', 'quantity', 'price', 'total_price')
    search_fields = ('id', 'order__id', 'store_item__product__name')
    ordering = ('-id', '-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'amount', 'transaction_id', 'reference_id', 'card_pan')
    list_filter = ('id', 'status',)
    search_fields = ('id', 'order__id', 'transaction_id', 'reference_id')
    ordering = ('-id', '-created_at',)


