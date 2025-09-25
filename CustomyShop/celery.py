import os

from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CustomyShop.settings.dev')

app = Celery('CustomyShop')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()



app.conf.beat_schedule = {
            'send_verify_payment_reminders': {
        'task': 'orders.tasks.send_verify_payment_reminders',
        'schedule': crontab(hour=9, minute=0), 
    },
    
    'weekly_cart_reminders': {
        'task': 'orders.tasks.send_weekly_cart_reminders',
        'schedule': crontab(hour=9, minute=0, day_of_week='mon'),  
    },
}