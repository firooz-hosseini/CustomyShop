from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import ProductImage
from stores.models import StoreItem
from accounts.models import Address

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class CartItemSerializer(serializers.ModelSerializer):
    store_item_id = serializers.IntegerField(source='store_item.id', read_only=True)
    product_id = serializers.IntegerField(source='store_item.product.id', read_only=True)
    product_name = serializers.ReadOnlyField(source='store_item.product.name')
    product_price = serializers.DecimalField(
        source='store_item.price', max_digits=10, decimal_places=2, read_only=True
    )
    product_image = ImageSerializer(source='store_item.product.image_product', many=True, read_only=True)
    product_category = serializers.ReadOnlyField(source='store_item.product.category.name')

    class Meta:
        model = CartItem
        fields = [
            'id', 'store_item_id', 'product_id',
            'product_name', 'product_price', 'quantity',
            'product_category', 'product_image', 'total_price'
        ]
        read_only_fields = ['total_price', 'product_name', 'product_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_cart', many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    total_discount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'subtotal', 'total_discount', 'total_price']


    def get_subtotal(self, obj):
        return sum(item.total_price for item in obj.cartitem_cart.all())

    def get_total_price(self, obj):
        return obj.total_price()

class AddToCartSerializer(serializers.Serializer):
    store_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_store_item_id(self, value):
        if not StoreItem.objects.filter(id=value).exists():
            raise serializers.ValidationError('StoreItem with this ID does not exist.')
        return value
    

class UpdateCartQuantitySerializer(serializers.Serializer):
    cart_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0) 

    def validate_cart_item_id(self, value):
        if not CartItem.objects.filter(id=value).exists():
            raise serializers.ValidationError("CartItem with this ID does not exist.")
        return value
    

class ApplyCartDiscountSerializer(serializers.Serializer):
    discount_value = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)



class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=[("online","Online"), ("cod","COD")], default="online")

    def validate_address_id(self, value):
        user = self.context["request"].user
        if not Address.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Address not found.")
        return value
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="store_item.product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "store_item", "product_name", "price", "quantity", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(source="orderitem_order", many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "address", "status", "total_price", "total_discount", "order_items"]
