from rest_framework import viewsets,permissions, status
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartQuantitySerializer
)
from .models import Cart, CartItem
from stores.models import StoreItem
from rest_framework.decorators import action
from rest_framework.response import Response


class CartApiView(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def list(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self.get_object()
        store_item = StoreItem.objects.get(id=serializer.validated_data['store_item_id'])
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(cart=cart, store_item=store_item)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        
        cart_item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)