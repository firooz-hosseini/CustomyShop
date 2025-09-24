from rest_framework import viewsets,permissions, status
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartQuantitySerializer,
    ApplyCartDiscountSerializer
)
from .models import Cart, CartItem
from stores.models import StoreItem
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

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
    @transaction.atomic
    def add_to_cart(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_object()
        store_item_id = serializer.validated_data['store_item_id']
        quantity = serializer.validated_data['quantity']

        try:
            store_item = StoreItem.objects.select_for_update().get(id=store_item_id)
        except StoreItem.DoesNotExist:
            return Response({'message': 'Store item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if store_item.stock <= 0:
            return Response({'message': 'This product is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity > store_item.stock:
            return Response(
                {'message': f'Only {store_item.stock} items available in stock.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

        cart_item, created = CartItem.objects.get_or_create(cart=cart, store_item=store_item)

        if cart_item.quantity + quantity > store_item.stock:
            return Response(
                {'message': f'You already have {cart_item.quantity} in your cart. '
                        f'Only {store_item.stock} total available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        
        cart_item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch'])
    @transaction.atomic
    def update_quantity(self, request):
        serializer = UpdateCartQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_object()
        cart_item_id = serializer.validated_data['cart_item_id']
        quantity = serializer.validated_data['quantity']

        cart_item = cart.cartitem_cart.filter(id=cart_item_id).first()

        if not cart_item:
            return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)
        store_item = StoreItem.objects.select_for_update().get(id=cart_item.store_item.id)

        if quantity > store_item.stock:
            return Response(
                {'message': f'Only {store_item.stock} items available in stock.'},
                status=400,
            )
        
        if quantity ==0:
            cart_item.delete()
            
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        return Response(CartSerializer(cart).data)
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        try:
            cart_item = cart.cartitem_cart.get(id=pk)
        except CartItem.DoesNotExist:
            return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):
        cart = self.get_object()
        cart.cartitem_cart.all().delete()
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=False, methods=['post'])
    def apply_discount(self, request):
        serializer = ApplyCartDiscountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_object()
        cart.total_discount = serializer.validated_data['discount_value']
        cart.save(update_fields=['total_discount'])

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)