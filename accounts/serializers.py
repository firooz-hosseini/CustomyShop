import re

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from .models import Address, CustomUser


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Request OTP Example',
            summary='Request OTP for a new user',
            description='User submits email, password, and optional info to get an OTP.',
            value={
                'email': 'john.doe@example.com',
                'password': 'Password123',
                'phone': '+1234567890',
                'first_name': 'John',
                'last_name': 'Doe',
            },
        )
    ]
)
class RequestOtpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

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


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Verify OTP Example',
            summary='Verify OTP code for registration',
            description='User submits email and OTP code to verify account and get JWT tokens.',
            value={'email': 'john.doe@example.com', 'otp_code': '123456'},
        )
    ]
)
class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, write_only=True)

    def validate_otp_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError('OTP must be a 6-digit number')
        return value


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Login Example',
            summary='User login with email and password',
            description='Returns access and refresh JWT tokens on success.',
            value={'email': 'john.doe@example.com', 'password': 'Password123'},
        )
    ]
)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Logout Example',
            summary='Logout using refresh token',
            description='Invalidate refresh token to logout from this device.',
            value={'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'},
        )
    ]
)
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Profile Example',
            summary='Retrieve or update user profile',
            description='Returns user info including email, phone, names, and profile image.',
            value={
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1234567890',
                'image': 'http://example.com/media/profile/john.png',
            },
        )
    ]
)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'image']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'User Address Example',
            summary='User address object',
            description='Used for retrieving, creating, or updating user addresses.',
            value={
                'id': 1,
                'user': 10,
                'store': None,
                'label': 'Home',
                'address_line_1': '123 Main Street',
                'address_line_2': 'Apt 4B',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
                'is_default': True,
            },
        )
    ]
)
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'store',
            'label',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'postal_code',
            'is_default',
        ]

        read_only_fields = [
            'id',
            'user',
            'store',
            'created_at',
            'updated_at',
            'is_deleted',
            'deleted_at',
        ]
