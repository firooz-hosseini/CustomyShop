from rest_framework import viewsets
from rest_framework import permissions
from .models import  Category, Product, ProductImage
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
