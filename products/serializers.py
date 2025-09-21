from rest_framework import serializers
from products.models import Product, Category, ProductImage

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context= self.context)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active', 'parent', 'children']

class ProductImageSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product', 'product_name']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    images = ProductImageSerializer(source="image_product", many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_name', 'images', 'is_active']
