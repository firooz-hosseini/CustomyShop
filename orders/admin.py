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


@admin.action(description="Approve selected orders (Processing)")
def make_processing(modeladmin, request, queryset):
    queryset.update(status=Order.PROCESSING)

@admin.action(description="Cancel selected orders")
def make_cancelled(modeladmin, request, queryset):
    for order in queryset:
        if order.status != Order.CANCELLED:
            order.status = Order.CANCELLED
            order.save()
            for item in order.orderitem_order.all():
                item.store_item.stock += item.quantity
                item.store_item.save()
    modeladmin.message_user(request, "Selected orders have been cancelled and stock restored.")

@admin.action(description="Mark selected orders as pending")
def make_pending(modeladmin, request, queryset):
    queryset.update(status=Order.PENDING)

@admin.action(description="Mark selected orders as delivered")
def make_delivered(modeladmin, request, queryset):
    queryset.update(status=Order.DELIVERED)

    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_price', 'total_discount')
    list_filter = ('id', 'status',)
    search_fields = ('id', 'customer__email', 'address__street')
    ordering = ('-id', '-created_at',)
    inlines = [OrderItemInline]
    actions = [make_processing, make_cancelled, make_pending]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'store_item', 'quantity', 'price', 'total_price')
    search_fields = ('id', 'order__id', 'store_item__product__name')
    ordering = ('-id', '-created_at',)


@admin.action(description="Mark selected payments as Successful")
def mark_payments_success(modeladmin, request, queryset):
    queryset.update(status=Payment.SUCCESS)

@admin.action(description="Mark selected payments as Failed")
def mark_payments_failed(modeladmin, request, queryset):
    for payment in queryset:
        payment.status = Payment.FAILED
        payment.save()

        order = payment.order
        if order.status != Order.CANCELLED:
            order.status = Order.CANCELLED
            order.save()

            for item in order.orderitem_order.all():
                item.store_item.stock += item.quantity
                item.store_item.save()
    modeladmin.message_user(request, "Selected payments failed; orders cancelled and stock restored.")

@admin.action(description="Mark selected payments as Pending")
def mark_payments_pending(modeladmin, request, queryset):
    queryset.update(status=Payment.PENDING)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'amount', 'transaction_id', 'reference_id', 'card_pan')
    list_filter = ('id', 'status',)
    search_fields = ('id', 'order__id', 'transaction_id', 'reference_id')
    ordering = ('-id', '-created_at',)
    actions = [mark_payments_success, mark_payments_failed, mark_payments_pending]


