from rest_framework import serializers
from .models import SellerRequest, Store, StoreItem
from accounts.models import CustomUser
from products.models import Product

class SellerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = ['id', 'user', 'status', 'created_at', 'reviewed_at']
        read_only_fields = ['user', 'status', 'created_at', 'reviewed_at']

class StoreSerializer(serializers.ModelSerializer):
    seller_email = serializers.ReadOnlyField(source='seller.email')

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'seller_email']

        read_only_fields= ['id', 'seller']


class StoreItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = StoreItem
        fields = ['id', 'stock', 'price', 'discount_price', 'is_active', 'product', 'product_name', 'store', 'store_name']

