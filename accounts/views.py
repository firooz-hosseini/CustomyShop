from rest_framework import viewsets, status
from .models import CustomUser
from .serializers import RequestOtpSerializer, VerifyOtpSerializer, LoginSerializer
from random import randint
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated


class RequestOtpApiView(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RequestOtpSerializer

    def create(self, request):
        serializer = RequestOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            phone = serializer.validated_data.get('phone')
            firs_name = serializer.validated_data.get('first_name')
            last_name = serializer.validated_data.get("last_name")


            otp_code = str(randint(100000,999999))
            cache.set(f'otp_{otp_code}', {
                'email': email,
                'password': password,
                'phone': phone,
                'firs_name': firs_name,
                'last_name': last_name,

            }, timeout=300)
            send_mail(
                subject='OTP code',
                message=f'Your OTP code: {otp_code}',
                from_email='firo744@gmail.com',
                recipient_list=[email],
            )
            return Response({'message': 'OTP is sent'}, status= status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyOtpApiView(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = VerifyOtpSerializer

    def create(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp_code']
            cached_data = cache.get(f'otp_{otp_code}')
            
            if not cached_data:
                return Response({'error': 'Invalid OTP'}, status = status.HTTP_400_BAD_REQUEST)
            
            email = cached_data.get('email')
            password = cached_data.get('password')
            phone = cached_data.get('phone','')
            first_name = cached_data.get("first_name",'')
            last_name = cached_data.get("last_name",'')

            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "phone": phone,
                    "first_name": first_name,
                    "last_name": last_name
                }
            )

            if created:
                user.set_password(password)
                user.save()

            cache.delete(f'otp_{otp_code}')

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User created successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginApiView(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }, status=status.HTTP_200_OK
                )
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutApiView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try: 
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out from this device'}, status=status.HTTP_200_OK)
        
        except TokenError:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
