from random import randint
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from .tasks import send_otp_email_task

def create_otp(email, password, phone='', first_name='', last_name=''):
    otp_code = str(randint(100000, 999999))

    cache.set(f'otp_{email}', {
        'otp_code': otp_code,
        'password': password,
        'phone': phone,
        'first_name': first_name,
        'last_name': last_name,
    }, timeout=300)

    send_otp_email_task.delay(email, otp_code)


def verify_otp(email, otp_code):
    cached_data = cache.get(f'otp_{email}')

    if not cached_data or cached_data.get('otp_code') != otp_code:
        return {
            'error': 'Invalid OTP'
        }

    email = email
    phone = cached_data.get('phone', '')
    first_name = cached_data.get('first_name', '')
    last_name = cached_data.get('last_name', '')

    user, created = get_user_model().objects.get_or_create(
        email=email,
        defaults={
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name
        }
    )

    if created:
        user.set_password(cached_data['password'])
        user.save()

    cache.delete(f'otp_{email}')

    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'created': created
    }


def login_user(email, password):
    user = authenticate(email=email, password=password)
    if not user:
        return None, 'Invalid email or password'

    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }, None


def logout_user(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as t:
        raise ValidationError(str(t))