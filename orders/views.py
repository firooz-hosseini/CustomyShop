from rest_framework import viewsets,permissions, status
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartQuantitySerializer,
    ApplyCartDiscountSerializer, 
    OrderSerializer, CheckoutSerializer
)
from .models import Cart, CartItem, Order, OrderItem, Payment
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
    


class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related("orderitem_order", "payment_order")

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        cart = Cart.objects.select_for_update().filter(user=request.user).first()
        if not cart or not cart.cartitem_cart.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        address_id = serializer.validated_data["address_id"]
        payment_method = serializer.validated_data["payment_method"]

        subtotal = 0
        total_discount = 0

        cart_items = list(cart.cartitem_cart.select_for_update().select_related("store_item__product"))

        for ci in cart_items:
            store_item = StoreItem.objects.select_for_update().get(pk=ci.store_item.pk)
            if ci.quantity > store_item.stock:
                return Response(
                    {"detail": f"Not enough stock for {store_item.product.name}. Available: {store_item.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            unit_price = store_item.discount_price if store_item.discount_price and store_item.discount_price > 0 else store_item.price
            subtotal += unit_price * ci.quantity

        cart_discount = getattr(cart, "total_discount", 0) or 0
        total_price = max(subtotal - cart_discount, 0)

        order = Order.objects.create(
            customer=request.user,
            address_id=address_id,
            total_price=total_price,
            total_discount=cart_discount,
            status=1 
        )

        for ci in cart_items:
            store_item = StoreItem.objects.get(pk=ci.store_item.pk)
            unit_price = store_item.discount_price if store_item.discount_price and store_item.discount_price > 0 else store_item.price

            OrderItem.objects.create(
                order=order,
                store_item=store_item,
                quantity=ci.quantity,
                price=unit_price
            )

            store_item.stock -= ci.quantity
            store_item.save(update_fields=["stock"])

        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            fee=0,
            status=1 
        )

        cart.cartitem_cart.all().delete()
        cart.total_discount = 0
        cart.save(update_fields=["total_discount"])

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def my_orders(self, request):
        qs = self.get_queryset().filter(customer=request.user)
        return Response(self.get_serializer(qs, many=True).data)