from rest_framework import serializers
from .models import SellerRequest, Store, StoreItem
from accounts.models import CustomUser, Address
from products.models import Product

class SellerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = ['id', 'user', 'status', 'created_at', 'reviewed_at']
        read_only_fields = ['user', 'status', 'created_at', 'reviewed_at']


class StoreAddressSerializer(serializers.ModelSerializer):
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = Address
        fields = [
            "id", "label", "address_line_1", "address_line_2",
            "city", "state", "country", "postal_code", 'is_default', "store", "store_name"
        ]
        read_only_fields = ["store"]


class StoreSerializer(serializers.ModelSerializer):
    seller_email = serializers.ReadOnlyField(source='seller.email')
    store_address = StoreAddressSerializer(source= 'address_store',read_only=True, many=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'seller_email', 'store_address']

        read_only_fields= ['id', 'seller']


class StoreItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = StoreItem
        fields = ['id', 'stock', 'price', 'discount_price', 'is_active', 'product', 'product_name', 'store', 'store_name']
        


