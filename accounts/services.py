from random import randint
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import CustomUser
from django.contrib.auth import authenticate


def create_otp(email, password, phone='', first_name='', last_name=''):
    otp_code = str(randint(100000, 999999))
    cache.set(f'otp_{otp_code}', {
        'email': email,
        'password': password,
        'phone': phone,
        'first_name': first_name,
        'last_name': last_name,
    }, timeout=300)

    send_mail(
        subject='OTP code',
        message=f'Your OTP code: {otp_code}',
        from_email='firo744@gmail.com',
        recipient_list=[email],
    )
    return otp_code


def verify_otp(otp_code):
    cached_data = cache.get(f'otp_{otp_code}')
    if not cached_data:
        return None, 'Invalid OTP'

    email = cached_data.get('email')
    password = cached_data.get('password')
    phone = cached_data.get('phone', '')
    first_name = cached_data.get('first_name', '')
    last_name = cached_data.get('last_name', '')

    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name
        }
    )

    if created:
        user.set_password(password)
        user.save()

    cache.delete(f'otp_{otp_code}')

    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'created': created
    }, None


def login_user(email, password):
    user = authenticate(email=email, password=password)
    if not user:
        return None, 'Invalid email or password'

    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, None


def logout_user(refresh_token):
    if not refresh_token:
        return 'Refresh token is required'

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return None
    except TokenError:
        return 'Invalid or expired token'