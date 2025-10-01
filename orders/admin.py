from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('store_item', 'quantity', 'total_price')
    readonly_fields = ('total_price',)
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'total_discount')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    inlines = [CartItemInline]

    def total_price(self, obj):
        return obj.total_price()
        
    total_price.short_description = "Total Price"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'store_item', 'quantity', 'total_price')
    search_fields = ('cart__user__email', 'store_item__product__name')
    ordering = ('-created_at',)

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = "Total Price"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('store_item', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)
    show_change_link = True


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('status', 'amount', 'transaction_id', 'reference_id', 'card_pan')
    readonly_fields = ('status', 'amount', 'transaction_id', 'reference_id', 'card_pan')
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_price', 'total_discount')
    list_filter = ('status',)
    search_fields = ('customer__email', 'address__street')
    ordering = ('-created_at',)
    inlines = [OrderItemInline, PaymentInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'store_item', 'quantity', 'price', 'total_price')
    search_fields = ('order__id', 'store_item__product__name')
    ordering = ('-created_at',)

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = "Total Price"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount', 'transaction_id', 'reference_id', 'card_pan')
    list_filter = ('status',)
    search_fields = ('order__id', 'transaction_id', 'reference_id')
    ordering = ('-created_at',)

