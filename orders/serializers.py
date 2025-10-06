from django.forms.models import model_to_dict
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from accounts.models import Address
from products.models import ProductImage
from stores.models import StoreItem

from .models import Cart, CartItem, Order, OrderItem


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class CartItemSerializer(serializers.ModelSerializer):
    store_item_id = serializers.IntegerField(source='store_item.id', read_only=True)
    product_id = serializers.IntegerField(
        source='store_item.product.id', read_only=True
    )
    product_name = serializers.ReadOnlyField(source='store_item.product.name')
    product_price = serializers.DecimalField(
        source='store_item.price', max_digits=10, decimal_places=2, read_only=True
    )
    product_image = ImageSerializer(
        source='store_item.product.image_product', many=True, read_only=True
    )
    product_category = serializers.ReadOnlyField(
        source='store_item.product.category.name'
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'store_item_id',
            'product_id',
            'product_name',
            'product_price',
            'quantity',
            'product_category',
            'product_image',
            'total_price',
        ]
        read_only_fields = ['total_price', 'product_name', 'product_price']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'CartItem Request Example',
            summary='Add item to cart',
            value={'store_item_id': 1, 'quantity': 2},
            request_only=True,
        ),
        OpenApiExample(
            'CartItem Response Example',
            summary='Cart item response',
            value={
                'id': 1,
                'store_item_id': 1,
                'product_id': 10,
                'product_name': 'Sample Product',
                'product_price': '100.00',
                'quantity': 2,
                'product_category': 'Electronics',
                'product_image': [
                    {'id': 1, 'image': 'http://example.com/media/products/1.png'}
                ],
                'total_price': '200.00',
            },
            response_only=True,
        ),
    ]
)
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_cart', many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    total_discount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
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
            raise serializers.ValidationError('CartItem with this ID does not exist.')
        return value


class ApplyCartDiscountSerializer(serializers.Serializer):
    discount_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=0
    )


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        user = self.context['request'].user
        if not Address.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError('Address not found.')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='store_item.product.name')

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'store_item',
            'product_name',
            'price',
            'quantity',
            'total_price',
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Checkout Request Example',
            summary='Checkout cart by providing address ID',
            value={'address_id': 1},
            request_only=True,
        ),
        OpenApiExample(
            'Order Response Example',
            summary='Full order details',
            value={
                'order': {
                    'id': 35,
                    'customer': 4,
                    'user_address': {
                        'id': 3,
                        'label': 'firooz',
                        'address_line_1': 'Bandar Abbas',
                        'address_line_2': 'null',
                        'city': 'Bandar Abbas',
                        'state': 'Hormozgan',
                        'country': 'Iran',
                        'postal_code': '9715421210',
                        'is_default': 'false',
                    },
                    'status': 1,
                    'total_price': '10000000.00',
                    'total_discount': '0.00',
                    'order_items': [
                        {
                            'id': 44,
                            'store_item': 28,
                            'product_name': 'Chocolate Shake',
                            'price': '10000000.00',
                            'quantity': 1,
                            'total_price': 10000000.0,
                        }
                    ],
                },
                'payment': {'id': 34, 'amount': 10000000.0, 'status': 0},
            },
            response_only=True,
        ),
    ]
)
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(
        source='orderitem_order', many=True, read_only=True
    )
    user_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'user_address',
            'status',
            'total_price',
            'total_discount',
            'order_items',
        ]

    def get_user_address(self, obj):
        if obj.address:
            return model_to_dict(
                obj.address, exclude=['user', 'store', 'is_deleted', 'deleted_at']
            )
        return None
