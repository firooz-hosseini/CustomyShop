from .base import *

DEBUG = os.getenv('DEBUG', True)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
CORS_ALLOW_ALL_ORIGINS = True