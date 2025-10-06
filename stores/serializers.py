from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from accounts.models import Address, CustomUser
from products.models import Product

from .models import SellerRequest, Store, StoreItem


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Seller Request Example",
            summary="Represents a user request to become a seller",
            value={
                "id": 1,
                "user": 5,
                "status": "pending",
                "created_at": "2025-10-02T12:00:00Z",
                "reviewed_at": None
            },
            response_only=True,
        )
    ]
)
class SellerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = ['id', 'user', 'status', 'created_at', 'reviewed_at']
        read_only_fields = ['user', 'status', 'created_at', 'reviewed_at']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Store Address Request Example",
            summary="Address for a store",
            value={
                "label": "Main Warehouse",
                "address_line_1": "123 Market Street",
                "address_line_2": "Suite 4B",
                "city": "Tehran",
                "state": "Tehran",
                "country": "Iran",
                "postal_code": "1234567890",
                "is_default": True,
                "store": 2,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Store Address Response Example",
            summary="Address for a store",
            value={
                "id": 1,
                "label": "Main Warehouse",
                "address_line_1": "123 Market Street",
                "address_line_2": "Suite 4B",
                "city": "Tehran",
                "state": "Tehran",
                "country": "Iran",
                "postal_code": "1234567890",
                "is_default": True,
                "store": 2,
                "store_name": "TechStore"
            },
            response_only=True,
        )
    ]
)
class StoreAddressSerializer(serializers.ModelSerializer):
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = Address
        fields = [
            'id',
            'label',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'postal_code',
            'is_default',
            'store',
            'store_name',
        ]
        read_only_fields = ['store']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Create Store Request Example',
            summary='Create or update Store',
            value={
                "name": "TechStore",
                "description": "Electronics and gadgets store"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Store Example",
            summary="Store object with addresses",
            value={
                "id": 2,
                "name": "TechStore",
                "description": "Electronics and gadgets store",
                "seller_email": "seller@example.com",
                "store_address": [
                    {
                        "id": 1,
                        "label": "Main Warehouse",
                        "address_line_1": "123 Market Street",
                        "address_line_2": "Suite 4B",
                        "city": "Tehran",
                        "state": "Tehran",
                        "country": "Iran",
                        "postal_code": "1234567890",
                        "is_default": True,
                        "store": 2,
                        "store_name": "TechStore"
                    }
                ]
                
            },
            response_only=True,
        )
    ]
)
class StoreSerializer(serializers.ModelSerializer):
    seller_email = serializers.ReadOnlyField(source='seller.email')
    store_address = StoreAddressSerializer(
        source='address_store', read_only=True, many=True
    )

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'seller_email', 'store_address']

        read_only_fields = ['id', 'seller']

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Store Item Example",
            summary="An item in the store",
            value={
                "stock": 100,
                "price": 499.99,
                "discount_price": 449.99,
                "is_active": True,
                "product": 10,
                "store": 2,
            },
            request_only=True,
        ),

        OpenApiExample(
            "Store Item Example",
            summary="An item in the store",
            value={
                "id": 5,
                "stock": 100,
                "price": 499.99,
                "discount_price": 449.99,
                "is_active": True,
                "product": 10,
                "product_name": "iPhone 15",
                "store": 2,
                "store_name": "TechStore"
            },
            response_only=True,
        )
    ]
)
class StoreItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = StoreItem
        fields = [
            'id',
            'stock',
            'price',
            'discount_price',
            'is_active',
            'product',
            'product_name',
            'store',
            'store_name',
        ]
