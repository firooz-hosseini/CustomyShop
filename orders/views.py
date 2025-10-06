import requests
from django.core.cache import cache
from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from stores.models import StoreItem

from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    AddToCartSerializer,
    ApplyCartDiscountSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
    PaymentStartSerializer,
    PaymentVerifySerializer,
    UpdateCartQuantitySerializer,
)
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

    def retrieve(self, request, pk=None):
        cart = self.get_object()
        try:
            cart_item = cart.cartitem_cart.get(id=pk)
        except CartItem.DoesNotExist:
            return Response(
                {'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @extend_schema(
        request=AddToCartSerializer,
        responses={201: CartSerializer},
        examples=[
            OpenApiExample(
                'Add to Cart - Request',
                value={'store_item_id': 1, 'quantity': 2},
                request_only=True,
            ),
            OpenApiExample(
                'Add to Cart - Response',
                value={
                    'id': 1,
                    'items': [
                        {
                            'id': 5,
                            'store_item_id': 1,
                            'product_id': 10,
                            'product_name': 'Wireless Mouse',
                            'product_price': '100.00',
                            'quantity': 2,
                            'product_category': 'Electronics',
                            'product_image': [
                                {
                                    'id': 1,
                                    'image': 'http://example.com/media/products/mouse.png',
                                }
                            ],
                            'total_price': '200.00',
                        }
                    ],
                    'subtotal': '200.00',
                    'total_discount': '0.00',
                    'total_price': '200.00',
                },
                response_only=True,
            ),
        ],
    )
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
            return Response(
                {'message': 'Store item not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        if store_item.stock <= 0:
            return Response(
                {'message': 'This product is out of stock.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity > store_item.stock:
            return Response(
                {'message': f'Only {store_item.stock} items available in stock.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, store_item=store_item
        )

        if cart_item.quantity + quantity > store_item.stock:
            return Response(
                {
                    'message': f'You already have {cart_item.quantity} in your cart. '
                    f'Only {store_item.stock} total available.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()
        cache.delete(f'cart:{request.user.id}')
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=UpdateCartQuantitySerializer,
        responses={200: CartSerializer},
        examples=[
            OpenApiExample(
                'Update Quantity - Request',
                value={'cart_item_id': 5, 'quantity': 3},
                request_only=True,
            ),
            OpenApiExample(
                'Update Quantity - Response',
                value={
                    'id': 1,
                    'items': [
                        {
                            'id': 5,
                            'store_item_id': 1,
                            'product_id': 10,
                            'product_name': 'Wireless Mouse',
                            'product_price': '100.00',
                            'quantity': 3,
                            'total_price': '300.00',
                        }
                    ],
                    'subtotal': '300.00',
                    'total_discount': '0.00',
                    'total_price': '300.00',
                },
                response_only=True,
            ),
        ],
    )
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
            return Response(
                {'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND
            )
        store_item = StoreItem.objects.select_for_update().get(
            id=cart_item.store_item.id
        )

        if quantity > store_item.stock:
            return Response(
                {'message': f'Only {store_item.stock} items available in stock.'},
                status=400,
            )

        if quantity == 0:
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
            return Response(
                {'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        cache.delete(f'cart:{request.user.id}')
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):
        cart = self.get_object()
        cart.cartitem_cart.all().delete()
        cache.delete(f'cart:{request.user.id}')
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=ApplyCartDiscountSerializer,
        responses={200: CartSerializer},
        examples=[
            OpenApiExample(
                'Apply Discount - Request',
                value={'discount_value': '25.00'},
                request_only=True,
            ),
            OpenApiExample(
                'Apply Discount - Response',
                value={
                    'id': 1,
                    'items': [
                        {
                            'id': 5,
                            'store_item_id': 1,
                            'product_id': 10,
                            'product_name': 'Wireless Mouse',
                            'product_price': '100.00',
                            'quantity': 3,
                            'total_price': '300.00',
                        }
                    ],
                    'subtotal': '300.00',
                    'total_discount': '25.00',
                    'total_price': '275.00',
                },
                response_only=True,
            ),
        ],
    )
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
        return Order.objects.filter(customer=self.request.user).prefetch_related(
            'orderitem_order', 'payment_order'
        )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        cart = Cart.objects.select_for_update().filter(user=request.user).first()
        if not cart or not cart.cartitem_cart.exists():
            return Response(
                {'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST
            )

        address_id = serializer.validated_data['address_id']
        if not address_id:
            return Response(
                {'detail': 'Address is required.'}, status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = list(
            cart.cartitem_cart.select_for_update().select_related('store_item__product')
        )

        subtotal = 0
        for item in cart_items:
            store_item = item.store_item
            if item.quantity > store_item.stock:
                return Response(
                    {
                        'detail': f'Not enough stock for {store_item.product.name}. Available: {store_item.stock}'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            unit_price = (
                store_item.discount_price
                if store_item.discount_price and store_item.discount_price > 0
                else store_item.price
            )
            subtotal += unit_price * item.quantity

        cart_discount = getattr(cart, 'total_discount', 0) or 0
        total_price = max(subtotal - cart_discount, 0)

        order = Order.objects.create(
            customer=request.user,
            address_id=address_id,
            total_price=total_price,
            total_discount=cart_discount,
            status=Order.PENDING,
        )

        for item in cart_items:
            store_item = item.store_item
            unit_price = (
                store_item.discount_price
                if store_item.discount_price and store_item.discount_price > 0
                else store_item.price
            )

            OrderItem.objects.create(
                order=order,
                store_item=store_item,
                quantity=item.quantity,
                price=unit_price,
            )

            store_item.stock -= item.quantity
            store_item.save(update_fields=['stock'])

        payment = Payment.objects.create(
            order=order, amount=order.total_price, fee=0, status=Payment.PENDING
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
            status=status.HTTP_201_CREATED,
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

    @extend_schema(
        tags=['Payments'],
        summary='Start Payment',
        description='Start the payment process for an order. Returns a payment URL and authority code if successful.',
        responses={
            200: OpenApiResponse(
                response=PaymentStartSerializer,
                description='Payment already started — existing link returned.',
                examples=[
                    OpenApiExample(
                        'Payment already started',
                        value={
                            'detail': 'Payment already started. Use existing link.',
                            'payment_url': 'https://sandbox.zarinpal.com/pg/StartPay/A000000000000000000000000000000000000',
                            'authority': 'A000000000000000000000000000000000000',
                            'amount': 120000,
                        },
                    )
                ],
            ),
            201: OpenApiResponse(
                response=PaymentStartSerializer,
                description='New payment successfully initiated.',
                examples=[
                    OpenApiExample(
                        'Successful start',
                        value={
                            'payment_url': 'https://sandbox.zarinpal.com/pg/StartPay/A111111111111111111111111111111111111',
                            'authority': 'A111111111111111111111111111111111111',
                            'amount': 150000,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=PaymentStartSerializer,
                description='Invalid payment data or amount too low.',
                examples=[
                    OpenApiExample(
                        'Invalid amount',
                        value={
                            'detail': 'Total price must be at least 1000 IRR to proceed.'
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                response=PaymentStartSerializer,
                description='Payment not found.',
                examples=[
                    OpenApiExample(
                        'Not found',
                        value={'detail': 'Payment not found.'},
                    )
                ],
            ),
            409: OpenApiResponse(
                response=PaymentStartSerializer,
                description='Payment already verified or failed previously.',
                examples=[
                    OpenApiExample(
                        'Already verified',
                        value={'detail': 'Payment already verified.'},
                    )
                ],
            ),
            502: OpenApiResponse(
                response=PaymentStartSerializer,
                description='Zarinpal did not return valid JSON or could not be reached.',
                examples=[
                    OpenApiExample(
                        'Gateway error',
                        value={'detail': 'Zarinpal did not return valid JSON'},
                    )
                ],
            ),
        },
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start(self, request, pk=None):
        payment = (
            Payment.objects.select_for_update()
            .filter(pk=pk, order__customer=request.user)
            .first()
        )
        if not payment:
            return Response(
                {'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        if payment.status == Payment.SUCCESS:
            serializer = PaymentStartSerializer({'detail': 'Payment already verified.'})
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)

        if payment.status == Payment.FAILED:
            serializer = PaymentStartSerializer(
                {'detail': 'Payment failed previously. Cannot restart.'}
            )
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)

        if payment.reference_id:
            serializer = PaymentStartSerializer(
                {
                    'detail': 'Payment already started. Use existing link.',
                    'payment_url': f'https://sandbox.zarinpal.com/pg/StartPay/{payment.reference_id}',
                    'authority': payment.reference_id,
                    'amount': int(payment.amount),
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        amount = int(payment.amount)
        if amount < 1000:
            serializer = PaymentStartSerializer(
                {'detail': 'Total price must be at least 1000 IRR to proceed.'}
            )
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        req_data = {
            'merchant_id': TEST_MERCHANT_ID,
            'amount': amount,
            'callback_url': request.build_absolute_uri(
                f'/api/payments/{payment.pk}/verify/'
            ),
            'description': f'Order #{payment.order.id}',
        }

        zarinpal_url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
        try:
            zarinpal_response = requests.post(zarinpal_url, json=req_data)
            response = zarinpal_response.json()
        except (ValueError, requests.exceptions.RequestException) as e:
            serializer = PaymentStartSerializer(
                {'detail': f'Failed to contact Zarinpal: {str(e)}'}
            )
            return Response(serializer.data, status=status.HTTP_502_BAD_GATEWAY)

        if response.get('data') and response['data'].get('code') == 100:
            authority = response['data']['authority']
            payment.reference_id = authority
            payment.save(update_fields=['reference_id'])

            serializer = PaymentStartSerializer(
                {
                    'payment_url': f'https://sandbox.zarinpal.com/pg/StartPay/{authority}',
                    'authority': authority,
                    'amount': amount,
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = PaymentStartSerializer(
            {
                'detail': 'Payment request failed',
                'amount': amount,
            }
        )
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Payments'],
        summary='Verify Payment',
        description='Verify the payment after the Zarinpal callback. Returns the transaction reference if successful.',
        responses={
            200: OpenApiResponse(
                response=PaymentVerifySerializer,
                description='Payment verified successfully.',
                examples=[
                    OpenApiExample(
                        'Successful verification',
                        value={
                            'detail': 'Payment verified successfully',
                            'ref_id': '123456789012345',
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=PaymentVerifySerializer,
                description='Payment cancelled or failed.',
                examples=[
                    OpenApiExample(
                        'Cancelled by user',
                        value={'detail': 'Payment was cancelled by user or gateway.'},
                    ),
                    OpenApiExample(
                        'Verification failed',
                        value={
                            'detail': 'Payment verification failed',
                            'zarinpal_response': {
                                'data': {'code': -21, 'message': 'Invalid authority'},
                            },
                        },
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=PaymentVerifySerializer,
                description='Payment not found.',
                examples=[
                    OpenApiExample(
                        'Not found',
                        value={'detail': 'Payment not found.'},
                    )
                ],
            ),
            409: OpenApiResponse(
                response=PaymentVerifySerializer,
                description='Payment already verified.',
                examples=[
                    OpenApiExample(
                        'Already verified',
                        value={
                            'detail': 'Payment already verified.',
                            'ref_id': '123456789012345',
                        },
                    )
                ],
            ),
            502: OpenApiResponse(
                response=PaymentVerifySerializer,
                description='Zarinpal response invalid or unreachable.',
                examples=[
                    OpenApiExample(
                        'Gateway error',
                        value={
                            'detail': 'Failed to contact Zarinpal: Timeout',
                        },
                    )
                ],
            ),
        },
    )
    @action(detail=True, methods=['get'])
    @transaction.atomic
    def verify(self, request, pk=None):
        payment = (
            Payment.objects.select_for_update()
            .filter(pk=pk)
            .select_related('order')
            .first()
        )
        if not payment:
            serializer = PaymentVerifySerializer({'detail': 'Payment not found.'})
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        if payment.status == Payment.SUCCESS:
            serializer = PaymentVerifySerializer(
                {
                    'detail': 'Payment already verified.',
                    'ref_id': payment.reference_id,
                }
            )
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)

        if not payment.reference_id:
            serializer = PaymentVerifySerializer({'detail': 'Payment not started.'})
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        callback_status = request.query_params.get('Status')
        if callback_status != 'OK':
            payment.status = Payment.FAILED
            payment.save(update_fields=['status'])
            serializer = PaymentVerifySerializer(
                {'detail': 'Payment was cancelled by user or gateway.'}
            )
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        verify_data = {
            'merchant_id': TEST_MERCHANT_ID,
            'amount': int(payment.amount),
            'authority': payment.reference_id,
        }

        verify_url = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
        try:
            verify_response = requests.post(verify_url, json=verify_data)
            response = verify_response.json()
        except (ValueError, requests.exceptions.RequestException) as e:
            serializer = PaymentVerifySerializer(
                {'detail': f'Failed to contact Zarinpal: {str(e)}'}
            )
            return Response(serializer.data, status=status.HTTP_502_BAD_GATEWAY)

        if response.get('data') and response['data'].get('code') == 100:
            payment.status = Payment.SUCCESS
            payment.transaction_id = response['data']['ref_id']
            payment.save(update_fields=['status', 'transaction_id'])

            order = payment.order
            if order.status not in [Order.CANCELLED, Order.DELIVERED]:
                order.status = Order.PROCESSING
                order.save(update_fields=['status'])

            payment_verified.send(sender=self.__class__, payment=payment)

            serializer = PaymentVerifySerializer(
                {
                    'detail': 'Payment verified successfully',
                    'ref_id': payment.transaction_id,
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        payment.status = Payment.FAILED
        payment.save(update_fields=['status'])
        serializer = PaymentVerifySerializer(
            {
                'detail': 'Payment verification failed',
                'zarinpal_response': response,
            }
        )
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
