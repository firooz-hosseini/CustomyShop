from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Address
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RequestOtpSerializer,
    UserAddressSerializer,
    VerifyOtpSerializer,
)
from .services import create_otp, login_user, logout_user, verify_otp
from .throttles import OtpRequestThrottle, OtpVerifyThrottle


class RequestOtpApiView(viewsets.GenericViewSet):
    serializer_class = RequestOtpSerializer
    throttle_classes = [OtpRequestThrottle]

    @extend_schema(
        request=RequestOtpSerializer,
        responses={
            200: OpenApiExample(
                'OTP Sent', value={'message': 'OTP is sent'}, response_only=True
            ),
            400: OpenApiExample(
                'Validation Error',
                value={'email': ['This field is required.']},
                response_only=True,
            ),
        },
        description='Request an OTP to register or login',
    )
    def create(self, request):
        serializer = RequestOtpSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            create_otp(
                email=data['email'],
                password=data['password'],
                phone=data.get('phone', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
            )
            return Response({'message': 'OTP is sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpApiView(viewsets.GenericViewSet):
    serializer_class = VerifyOtpSerializer
    throttle_classes = [OtpVerifyThrottle]

    @extend_schema(
        request=VerifyOtpSerializer,
        responses={
            201: OpenApiExample(
                'User Created',
                value={
                    'message': 'User created successfully',
                    'access': 'access_token_here',
                    'refresh': 'refresh_token_here',
                },
                response_only=True,
            ),
            400: OpenApiExample(
                'Invalid OTP', value={'error': 'Invalid OTP'}, response_only=True
            ),
        },
        description='Verify the OTP sent to the user and create the account if needed',
    )
    def create(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']

            result = verify_otp(email=email, otp_code=otp_code)

            if 'error' in result:
                return Response(
                    {'error': result['error']}, status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    'message': 'User created successfully',
                    'access': result['access'],
                    'refresh': result['refresh'],
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiExample(
                'Login Successful',
                value={
                    'message': 'Login successful',
                    'access': 'access_token_here',
                    'refresh': 'refresh_token_here',
                },
                response_only=True,
            ),
            401: OpenApiExample(
                'Invalid Credentials',
                value={'error': 'Invalid email or password'},
                response_only=True,
            ),
        },
        description='Login user and return JWT access/refresh tokens',
    )
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            result, error = login_user(email, password)
            if error:
                return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)

            return Response(
                {
                    'message': 'Login successful',
                    'access': result['access'],
                    'refresh': result['refresh'],
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutApiView(viewsets.GenericViewSet):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: OpenApiExample(
                'Logout Successful',
                value={'message': 'Successfully logged out from this device'},
                response_only=True,
            ),
            400: OpenApiExample(
                'Invalid Token',
                value={'detail': 'Token is invalid or expired'},
                response_only=True,
            ),
        },
        description='Logout user by blacklisting the refresh token',
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get('refresh_token')
        logout_user(refresh_token)

        return Response(
            {'message': 'Successfully logged out from this device'},
            status=status.HTTP_200_OK,
        )


class ProfileApiView(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ProfileSerializer, description="Get or update current user's profile"
    )
    @action(detail=False, methods=['get', 'put', 'patch'])
    def myuser(self, request):
        if request.method == 'GET':
            serializer = ProfileSerializer(request.user)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = ProfileSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = ProfileSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class UserAddressApiView(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserAddressSerializer,
        responses=UserAddressSerializer,
        description="CRUD operations for user's addresses",
    )
    def get_queryset(self):
        user = self.request.user
        user_addresses = Address.objects.filter(user=user)
        return user_addresses

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
