from celery import shared_task
from django.core.mail import send_mail
from .models import Payment, Cart
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import os

@shared_task
def send_verify_payment_reminders():
    now = timezone.now()
    pending_payments = Payment.objects.filter(
        status=Payment.PENDING,
        created_at__lte=now - timedelta(days=1)
    ).select_related('order', 'order__customer')

    reminders = defaultdict(list)
    for payment in pending_payments:
        user = payment.order.customer
        reminders[user].append(payment)

    for user, payments in reminders.items():
        payment_texts = [f"- Order #{p.order.id} ({p.amount} USD)" for p in payments]
        email_body = "You have pending payments:\n" + "\n".join(payment_texts)
        send_mail(
            subject="Reminder: Pending Payments",
            message=email_body,
            from_email=os.getenv('EMAIL_HOST_USER', ''),
            recipient_list=[user.email],
        )


@shared_task
def send_weekly_cart_reminders():

    carts = Cart.objects.filter(cartitem_cart__isnull=False).select_related('user').distinct()

    for cart in carts:
        user = cart.user
        email_body = (
            "You have items in your cart that haven't been checked out yet. "
            "Complete your order before they're sold out!"
        )
        send_mail(
            subject="Reminder: Items in Your Cart",
            message=email_body,
            from_email=os.getenv('EMAIL_HOST_USER', ''),
            recipient_list=[user.email],
        )
