from django.dispatch import Signal, receiver
from .tasks import send_payment_success_email_task

payment_verified = Signal()

@receiver(payment_verified)
def send_payment_success_email(sender, payment, **kwargs):
    
    order = payment.order
    subject = f'Payment Successful - Order #{order.id}'
    message = (
        f'Hello {order.customer.first_name or order.customer.email},\n\n'
        f'Your payment for Order #{order.id} was successful.\n'
        f'Transaction ID: {payment.transaction_id}\n'
        f'Amount: {payment.amount}\n\n'
        'Thank you for shopping with us!'
    )
    recipient = [order.customer.email]

    send_payment_success_email_task.delay(subject, message, recipient)