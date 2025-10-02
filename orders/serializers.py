from django.forms.models import model_to_dict
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from accounts.models import Address
from products.models import ProductImage
from stores.models import StoreItem

from .models import Cart, CartItem, Order, OrderItem


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Product Image Response Example',
            summary='Product image object',
            value={'id': 1, 'image': 'http://example.com/media/products/1.png'},
            response_only=True,
        )
    ]
)
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


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
            'Cart Response Example',
            summary='Full cart object with items',
            value={
                'id': 1,
                'items': [
                    {
                        'id': 1,
                        'store_item_id': 1,
                        'product_id': 10,
                        'product_name': 'Sample Product',
                        'product_price': '100.00',
                        'quantity': 2,
                        'product_category': 'Electronics',
                        'product_image': [
                            {
                                'id': 1,
                                'image': 'http://example.com/media/products/1.png',
                            }
                        ],
                        'total_price': '200.00',
                    }
                ],
                'subtotal': '200.00',
                'total_discount': '20.00',
                'total_price': '180.00',
            },
            response_only=True,
        )
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


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'AddToCart Request Example',
            summary='Add a store item to cart',
            value={'store_item_id': 1, 'quantity': 2},
            request_only=True,
        )
    ]
)
class AddToCartSerializer(serializers.Serializer):
    store_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_store_item_id(self, value):
        if not StoreItem.objects.filter(id=value).exists():
            raise serializers.ValidationError('StoreItem with this ID does not exist.')
        return value


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'UpdateCartQuantity Request Example',
            summary='Update quantity of cart item',
            value={'cart_item_id': 1, 'quantity': 3},
            request_only=True,
        )
    ]
)
class UpdateCartQuantitySerializer(serializers.Serializer):
    cart_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)

    def validate_cart_item_id(self, value):
        if not CartItem.objects.filter(id=value).exists():
            raise serializers.ValidationError('CartItem with this ID does not exist.')
        return value


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'ApplyCartDiscount Request Example',
            summary='Apply a discount to the cart',
            value={'discount_value': '20.00'},
            request_only=True,
        )
    ]
)
class ApplyCartDiscountSerializer(serializers.Serializer):
    discount_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=0
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Checkout Request Example',
            summary='Checkout cart by providing address ID',
            value={'address_id': 1},
            request_only=True,
        )
    ]
)
class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        user = self.context['request'].user
        if not Address.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError('Address not found.')
        return value


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'OrderItem Response Example',
            summary='Order item details',
            value={
                'id': 1,
                'store_item': 1,
                'product_name': 'Sample Product',
                'price': '100.00',
                'quantity': 2,
                'total_price': '200.00',
            },
            response_only=True,
        )
    ]
)
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
            'Order Response Example',
            summary='Full order details',
            value={
                'id': 1,
                'customer': 10,
                'user_address': {
                    'id': 1,
                    'label': 'Home',
                    'address_line_1': '123 Main Street',
                    'city': 'New York',
                    'state': 'NY',
                    'country': 'USA',
                    'postal_code': '10001',
                },
                'status': 'PENDING',
                'total_price': '180.00',
                'total_discount': '20.00',
                'order_items': [
                    {
                        'id': 1,
                        'store_item': 1,
                        'product_name': 'Sample Product',
                        'price': '100.00',
                        'quantity': 2,
                        'total_price': '200.00',
                    }
                ],
            },
            response_only=True,
        )
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
