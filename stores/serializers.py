from rest_framework import serializers
from .models import SellerRequest

class SellerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = ['id', 'user', 'status', 'created_at', 'reviewed_at']
        read_only_fields = ['user', 'status', 'created_at', 'reviewed_at']