from rest_framework import serializers
from .models import CustomUser

class RequestOtpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'mobile', 'first_name', 'last_name']
