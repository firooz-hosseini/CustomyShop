from django.dispatch import Signal, receiver
from django.core.mail import send_mail
from django.conf import settings

payment_verified = Signal()

@receiver(payment_verified)
def send_payment_success_email(sender, payment, **kwargs):
    
    order = payment.order
    subject = f'Payment Successful - Order #{order.id}'
    message = (
        f'Hello {order.customer.username},\n\n'
        f'Your payment for Order #{order.id} was successful.\n'
        f'Transaction ID: {payment.transaction_id}\n'
        f'Amount: {payment.amount}\n\n'
        'Thank you for shopping with us!'
    )
    recipient = [order.customer.email]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient,
        fail_silently=False,
    )