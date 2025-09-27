from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser


@shared_task
def send_welcome_email_task(user_id):

    user = CustomUser.objects.get(pk=user_id)

    subject = 'Welcome to our site!'
    message = f'Hi {user.first_name}, thanks for signing up.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    return {'status': 'sent', 'user': user_id}


@shared_task
def send_otp_email_task(email, otp_code):
        send_mail(
        subject='Your OTP Code',
        message=f'Your OTP code is: {otp_code}',
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
