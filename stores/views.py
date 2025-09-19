from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SellerRequest
from .serializers import SellerRequestSerializer

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
        if SellerRequest.objects.filter(user=request.user, status='pending').exists():
            return Response({"detail": "You already have a pending request."}, status=400)

        seller_request = SellerRequest.objects.create(user=request.user)
        serializer = self.get_serializer(seller_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)