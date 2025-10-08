import os

from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Count, Q

from .models import Cart, Order, Payment


@shared_task
def send_unpaid_order_reminders():
    unpaid_orders = Order.objects.filter(
        status=Order.PENDING,
        payment_order__status=Payment.PENDING,
    ).select_related('customer')

    for order in unpaid_orders:
        user = order.customer
        subject = f'Reminder: Your order #{order.id} is still unpaid'
        message = (
            f'Dear {user.first_name or user.email},\n\n'
            f"You placed order #{order.id} but haven't completed the payment yet.\n"
            f'Total amount: {order.total_price} IRR.\n\n'
            f'Please visit your account to complete the payment.\n\n'
            'Thank you for shopping with us!'
        )
        send_mail(subject, message, os.getenv('EMAIL_HOST_USER', ''), [user.email])

    return f'Sent {unpaid_orders.count()} unpaid order reminders.'


@shared_task
def send_cart_reminders():
    inactive_carts = (
        Cart.objects.annotate(
            item_count=Count('cartitem_cart', filter=Q(cartitem_cart__is_deleted=False))
        )
        .filter(item_count__gt=0)
        .select_related('user')
    )

    for cart in inactive_carts:
        user = cart.user
        subject = 'You still have items waiting in your cart '
        message = (
            f'Hi {user.first_name or user.email},\n\n'
            'We noticed you added items to your cart but haven’t checked out yet.\n'
            'Come back and complete your purchase before your favorite items run out!\n\n'
            'Visit your cart now to finish your order.'
        )
        send_mail(subject, message, os.getenv('EMAIL_HOST_USER', ''), [user.email])

    return f'Sent {inactive_carts.count()} cart reminders.'


@shared_task
def send_payment_success_email_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        os.getenv('EMAIL_HOST_USER', ''),
        recipient_list,
        fail_silently=False,
    )
