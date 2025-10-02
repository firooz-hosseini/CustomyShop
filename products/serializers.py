from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from products.models import Category, Product, ProductImage


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Category Example',
            summary='Example of a category with children',
            description='Shows a category including nested children categories',
            value={
                'id': 2,
                'name': 'Smartphones',
                'description': 'All mobile phones',
                'image': 'http://example.com/media/category/smartphones.png',
                'is_active': True,
                'parent': 1,
                'children': [
                    {
                        'id': 3,
                        'name': 'Android Phones',
                        'description': 'All Android devices',
                        'image': 'http://example.com/media/category/android.png',
                        'is_active': True,
                        'parent': 2,
                        'children': [],
                    }
                ],
            },
        )
    ]
)
class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'image',
            'is_active',
            'parent',
            'children',
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Product Image Example',
            summary='Product image object',
            description='Represents an image associated with a product.',
            value={
                'id': 10,
                'image': 'http://example.com/media/product/product1.jpg',
                'product': 5,
                'product_name': 'iPhone 15',
            },
        )
    ]
)
class ProductImageSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product', 'product_name']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Product Example',
            summary='Product object with images',
            description='Represents a product with optional images and category info.',
            value={
                'id': 5,
                'name': 'iPhone 15',
                'description': 'Latest Apple smartphone',
                'category': 1,
                'category_name': 'Electronics',
                'images': [
                    {
                        'id': 10,
                        'image': 'http://example.com/media/product/product1.jpg',
                        'product': 5,
                        'product_name': 'iPhone 15',
                    },
                    {
                        'id': 11,
                        'image': 'http://example.com/media/product/product2.jpg',
                        'product': 5,
                        'product_name': 'iPhone 15',
                    },
                ],
                'is_active': True,
            },
        )
    ]
)
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    images = ProductImageSerializer(source='image_product', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'category',
            'category_name',
            'images',
            'is_active',
        ]
