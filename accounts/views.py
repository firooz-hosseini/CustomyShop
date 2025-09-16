from rest_framework import viewsets, status
from .models import CustomUser
from .serializers import RequestOtpSerializer, VerifyOtpSerializer, LoginSerializer, LogoutSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .throttles import OtpRequestThrottle, OtpVerifyThrottle
from .services import create_otp, verify_otp, login_user, logout_user


class RequestOtpApiView(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RequestOtpSerializer
    throttle_classes = [OtpRequestThrottle]

    def create(self, request):
        serializer = RequestOtpSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            create_otp(
                email=data['email'],
                password=data['password'],
                phone=data.get('phone', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            return Response({'message': 'OTP is sent'}, status= status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyOtpApiView(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = VerifyOtpSerializer
    throttle_classes = [OtpVerifyThrottle]

    def create(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']

            result = verify_otp(email=email, otp_code=otp_code)
            
            if 'error' in result:   
                return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'message': 'User created successfully',
                'refresh': result['refresh'],
                'access': result['access']
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginApiView(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            result, error = login_user(email, password)
            if error:
                return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({
                    'message': 'Login successful',
                    'refresh': result['refresh'],
                    'access': result['access']
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutApiView(viewsets.GenericViewSet):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get('refresh_token')
        logout_user(refresh_token)

        return Response({'message': 'Successfully logged out from this device'}, status=status.HTTP_200_OK)
    