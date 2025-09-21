from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel


class CustomUserManager(BaseUserManager):

    def create_user(self,email,password,**kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_staff", True) 
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        return self.create_user(email, password, **kwargs)

class CustomUser(AbstractUser, BaseModel):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]

    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='user/', null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES, default='customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Address(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='address_user', blank=True, null=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='address_store', blank=True, null=True)
    label = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.label} - {self.city}'


    