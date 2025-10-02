from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import ProductFilter
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductImageSerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            200: OpenApiExample(
                'Category List',
                value=[
                    {
                        'id': 1,
                        'name': 'Electronics',
                        'description': 'Devices and gadgets',
                        'image': 'http://example.com/media/categories/electronics.png',
                        'is_active': True,
                        'parent': None,
                        'children': [],
                    }
                ],
                response_only=True,
            )
        },
        description='Retrieve all categories. Includes recursive children categories.',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: OpenApiExample(
                'Category Detail',
                value={
                    'id': 1,
                    'name': 'Electronics',
                    'description': 'Devices and gadgets',
                    'image': 'http://example.com/media/categories/electronics.png',
                    'is_active': True,
                    'parent': None,
                    'children': [
                        {
                            'id': 2,
                            'name': 'Smartphones',
                            'description': 'Mobile phones',
                            'image': None,
                            'is_active': True,
                            'parent': 1,
                            'children': [],
                        }
                    ],
                },
                response_only=True,
            )
        },
        description='Retrieve details of a single category',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'description']
    filterset_class = ProductFilter
    ordering_fields = ['name']
    ordering = ['id']

    def get_permissions(self):
        if self.action in [
            'create',
            'update',
            'partial_update',
            'destroy',
            'upload_image',
        ]:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @extend_schema(
        request=ProductSerializer,
        responses={
            200: OpenApiExample(
                'Product List',
                value=[
                    {
                        'id': 1,
                        'name': 'iPhone 15',
                        'description': 'Latest Apple iPhone',
                        'category': 2,
                        'category_name': 'Smartphones',
                        'images': [
                            {
                                'id': 1,
                                'image': 'http://example.com/media/products/iphone15.png',
                                'product': 1,
                                'product_name': 'iPhone 15',
                            }
                        ],
                        'is_active': True,
                    }
                ],
                response_only=True,
            )
        },
        description='List all products (supports search, filtering, and ordering)',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=ProductSerializer,
        responses={
            201: OpenApiExample(
                'Product Created',
                value={
                    'id': 10,
                    'name': 'Samsung Galaxy S24',
                    'description': 'Flagship Samsung phone',
                    'category': 2,
                    'category_name': 'Smartphones',
                    'images': [],
                    'is_active': True,
                },
                response_only=True,
            )
        },
        description='Create a new product (Admin only)',
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: OpenApiExample(
                'Product Detail',
                value={
                    'id': 1,
                    'name': 'iPhone 15',
                    'description': 'Latest Apple iPhone',
                    'category': 2,
                    'category_name': 'Smartphones',
                    'images': [
                        {
                            'id': 1,
                            'image': 'http://example.com/media/products/iphone15.png',
                            'product': 1,
                            'product_name': 'iPhone 15',
                        }
                    ],
                    'is_active': True,
                },
                response_only=True,
            )
        },
        description='Retrieve details of a single product',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        request=ProductImageSerializer,
        responses={
            200: OpenApiExample(
                'Product Image List',
                value=[
                    {
                        'id': 1,
                        'image': 'http://example.com/media/products/iphone15.png',
                        'product': 1,
                        'product_name': 'iPhone 15',
                    }
                ],
                response_only=True,
            )
        },
        description='List all product images',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=ProductImageSerializer,
        responses={
            201: OpenApiExample(
                'Product Image Created',
                value={
                    'id': 5,
                    'image': 'http://example.com/media/products/s24.png',
                    'product': 10,
                    'product_name': 'Samsung Galaxy S24',
                },
                response_only=True,
            )
        },
        description='Upload a new product image (Admin only)',
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
