from rest_framework import viewsets, status
from .models import CustomUser
from .serializers import RequestOtpSerializer
from random import randint
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.response import Response


class RequestOtpView(viewsets.GenericViewSet):
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





            


