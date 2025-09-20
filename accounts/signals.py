from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser
from .tasks import send_welcome_email_task

@receiver(post_save, sender=CustomUser)
def send_welcome_email_signal(sender, instance, created, **kwargs):
    if created:
        send_welcome_email_task.delay_on_commit(instance.pk)