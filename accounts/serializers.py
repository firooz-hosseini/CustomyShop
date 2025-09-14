from rest_framework import serializers
from .models import CustomUser

class RequestOtpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'phone', 'first_name', 'last_name']


class VerifyOtpSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6,write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)

    