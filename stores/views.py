from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from .models import SellerRequest, Store, StoreItem
from .serializers import SellerRequestSerializer, StoreSerializer, StoreItemSerializer, StoreAddressSerializer
from accounts.models import Address
from .permissions import IsOwnerOrAdmin
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied



class SellerRequestViewSet(viewsets.GenericViewSet):
    serializer_class = SellerRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SellerRequest.objects.all()
        return SellerRequest.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if SellerRequest.objects.filter(user=request.user).exclude(status='rejected').exists():
            return Response({'detail': 'You already have a seller request (pending or approved).'}, status=status.HTTP_400_BAD_REQUEST)

        seller_request = SellerRequest.objects.create(user=request.user)
        serializer = self.get_serializer(seller_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class StoreApiViewSet(viewsets.ModelViewSet):

    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Store.objects.all()
        return Store.objects.filter(seller=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'seller':
            raise PermissionDenied('You are not a seller.')

        if not SellerRequest.objects.filter(user=user, status=SellerRequest.APPROVED).exists():
            raise PermissionDenied('Your seller request has not been approved yet.')

        if Store.objects.filter(seller=user).exists():
            raise PermissionDenied('You already have a store.')

        serializer.save(seller=user)


class StoreItemApiViewSet(viewsets.ModelViewSet):
    serializer_class = StoreItemSerializer

    def get_queryset(self):
        user = self.request.user
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if user.is_staff:
                return StoreItem.objects.all()
            return StoreItem.objects.filter(store__seller=user)
        else:
            return StoreItem.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
        

    def perform_create(self, serializer):
        user = self.request.user
        store = serializer.validated_data.get('store')

        if not user.is_staff and store.seller != user:
            raise PermissionDenied('You can only add items to your own store.')

        serializer.save(store=store)

    def perform_update(self, serializer):
        user = self.request.user
        store = serializer.instance.store

        if not user.is_staff and store.seller != user:
            raise PermissionDenied('You can only update items in your own store.')

        serializer.save(product=serializer.instance.product, store=store)

    def perform_destroy(self, instance):
        user = self.request.user
        store = instance.store

        if not user.is_staff and store.seller != user:
            raise PermissionDenied('You can only delete items from your own store.')

        instance.delete()


class StoreAddressApiView(viewsets.ModelViewSet):
    serializer_class = StoreAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(store__seller=user)

    def perform_create(self, serializer):
        user = self.request.user
        store_id = self.request.data.get('store_id')
        if not store_id:
            raise ValueError('store_id is required to create an address.')

        store = get_object_or_404(Store, id=store_id, seller=user)
        serializer.save(store=store)