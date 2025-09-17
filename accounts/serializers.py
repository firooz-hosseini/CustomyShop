from rest_framework import serializers
from .models import CustomUser
import re


class RequestOtpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 8)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'phone', 'first_name', 'last_name']

    def validate_password(self, value):
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value):
            raise serializers.ValidationError(
                'Password must contain at least one letter and one number'
            )
        return value
    
    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('First name must contain only letters')
        return value
    
    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('Last name must contain only letters')
        return value
    

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6,write_only=True)

    def validate_otp_code(self, value):
        if not value.isdigit() or len(value) !=6:
            raise serializers.ValidationError('OTP must be a 6-digit number')
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone' , 'image']