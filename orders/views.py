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
import requests
from django.core.cache import cache
from .signals import payment_verified

class CartApiView(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        user_id = self.request.user.id
        cache_key = f'cart:{user_id}'

        cached_cart = cache.get(cache_key)
        if cached_cart:
            try:
                return Cart.objects.only('id', 'user').get(id=cached_cart['id'])
            except Cart.DoesNotExist:
                cache.delete(cache_key)
        
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        cache.set(cache_key, {'id': cart.id}, timeout=300) 
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
        cache.delete(f'cart:{request.user.id}')
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
            cache.delete(f'cart:{request.user.id}')
        
        return Response(CartSerializer(cart).data)
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        try:
            cart_item = cart.cartitem_cart.get(id=pk)
        except CartItem.DoesNotExist:
            return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        cache.delete(f'cart:{request.user.id}')
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):
        cart = self.get_object()
        cart.cartitem_cart.all().delete()
        cache.delete(f'cart:{request.user.id}')
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=False, methods=['post'])
    def apply_discount(self, request):
        serializer = ApplyCartDiscountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_object()
        cart.total_discount = serializer.validated_data['discount_value']
        cart.save(update_fields=['total_discount'])
        cache.delete(f'cart:{request.user.id}')

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    


class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related('orderitem_order', 'payment_order')

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        cart = Cart.objects.select_for_update().filter(user=request.user).first()
        if not cart or not cart.cartitem_cart.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        address_id = serializer.validated_data['address_id']
        if not address_id:
            return Response({'detail': 'Address is required.'}, status=status.HTTP_400_BAD_REQUEST)


        cart_items = list(
            cart.cartitem_cart.select_for_update().select_related('store_item__product')
        )

        subtotal = 0
        for item in cart_items:
            store_item = item.store_item
            if item.quantity > store_item.stock:
                return Response(
                    {'detail': f'Not enough stock for {store_item.product.name}. Available: {store_item.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            unit_price = store_item.discount_price if store_item.discount_price and store_item.discount_price > 0 else store_item.price
            subtotal += unit_price * item.quantity

        cart_discount = getattr(cart, 'total_discount', 0) or 0
        total_price = max(subtotal - cart_discount, 0)

        order = Order.objects.create(
            customer=request.user,
            address_id=address_id,
            total_price=total_price,
            total_discount=cart_discount,
            status=Order.PENDING
        )

        for item in cart_items:
            store_item = item.store_item
            unit_price = store_item.discount_price if store_item.discount_price and store_item.discount_price > 0 else store_item.price

            OrderItem.objects.create(
                order=order,
                store_item=store_item,
                quantity=item.quantity,
                price=unit_price
            )

            store_item.stock -= item.quantity
            store_item.save(update_fields=['stock'])

        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            fee=0,
            status=Payment.PENDING
        )

        cart.cartitem_cart.all().delete()
        cart.total_discount = 0
        cart.save(update_fields=['total_discount'])
        cache.delete(f'cart:{request.user.id}')
        cache.delete(f'orders:{request.user.id}')
        
        return Response(
            {
                'message': 'Checkout successful. Proceed to payment.',
                'order': OrderSerializer(order).data,
                'payment': {
                    'id': payment.id,
                    'amount': payment.amount,
                    'status': payment.status,
                },
            },
            status=status.HTTP_201_CREATED
        )
    

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        user_id = request.user.id
        cache_key = f'orders:{user_id}'

        cached_orders = cache.get(cache_key)
        if cached_orders:
            return Response(cached_orders)
        
        queryset = self.get_queryset().filter(customer=request.user)
        serialized = self.get_serializer(queryset, many=True).data

        cache.set(cache_key, serialized, timeout=300)

        return Response(serialized)
    

TEST_MERCHANT_ID = '00000000-0000-0000-0000-000000000000'

class PaymentViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start(self, request, pk=None):

        payment = Payment.objects.select_for_update().filter(pk=pk, order__customer=request.user).first()
        if not payment:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == Payment.SUCCESS:
            return Response({'detail': 'Payment already verified.'}, status=status.HTTP_409_CONFLICT)

        if payment.status == Payment.FAILED:
            return Response({'detail': 'Payment failed previously. Cannot restart.'}, status=status.HTTP_409_CONFLICT)

        if payment.reference_id:
            return Response({
                'detail': 'Payment already started. Use existing link.',
                'payment_url': f'https://sandbox.zarinpal.com/pg/StartPay/{payment.reference_id}',
                'authority': payment.reference_id,
            }, status=status.HTTP_200_OK)


        amount = int(payment.amount)
        if amount < 1000:
            return Response({'detail': 'Total price must be at least 1000 IRR to proceed.'}, status=status.HTTP_400_BAD_REQUEST)

        req_data = {
            'merchant_id': TEST_MERCHANT_ID,
            'amount': amount,
            'callback_url': request.build_absolute_uri(f'/api/payments/{payment.pk}/verify/'),
            'description': f'Order #{payment.order.id}',
        }

        zarinpal_url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
        try:
            zarinpal_response = requests.post(zarinpal_url, json=req_data)
            response = zarinpal_response.json()
        except ValueError:
            return Response({'detail': 'Zarinpal did not return valid JSON', 'raw': zarinpal_response.text}, status=status.HTTP_502_BAD_GATEWAY)

        if response.get('data') and response['data'].get('code') == 100:
            authority = response['data']['authority']
            payment.reference_id = authority
            payment.save(update_fields=['reference_id'])
            return Response({
                'payment_url': f'https://sandbox.zarinpal.com/pg/StartPay/{authority}',
                'authority': authority,
                'amount': amount,
            })

        return Response({'detail': 'Payment request failed', 'zarinpal_response': response}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'])
    @transaction.atomic
    def verify(self, request, pk=None):
        payment = Payment.objects.select_for_update().filter(pk=pk).select_related('order').first()
        if not payment:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == Payment.SUCCESS:
            return Response({'detail': 'Payment already verified.', 'ref_id': payment.reference_id}, status=status.HTTP_409_CONFLICT)

        if not payment.reference_id:
            return Response({'detail': 'Payment not started.'}, status=status.HTTP_400_BAD_REQUEST)

        verify_data = {
            'merchant_id': TEST_MERCHANT_ID,
            'amount': int(payment.amount),
            'authority': payment.reference_id,
        }

        verify_url = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
        try:
            verify_response = requests.post(verify_url, json=verify_data)
            response = verify_response.json()
        except ValueError:
            return Response({'detail': 'Zarinpal did not return valid JSON', 'raw': verify_response.text}, status=status.HTTP_502_BAD_GATEWAY)

        if response.get('data') and response['data'].get('code') == 100:
            payment.status = Payment.SUCCESS
            payment.transaction_id = response['data']['ref_id']
            payment.save(update_fields=['status', 'transaction_id'])

            order = payment.order
            order.status = Order.PROCESSING
            order.save(update_fields=['status'])
            
            payment_verified.send(sender=self.__class__, payment=payment)
            
            return Response({'detail': 'Payment verified successfully', 'ref_id': payment.transaction_id})

        payment.status = Payment.FAILED
        payment.save(update_fields=['status'])
        return Response({'detail': 'Payment verification failed', 'zarinpal_response': response}, status=status.HTTP_400_BAD_REQUEST)