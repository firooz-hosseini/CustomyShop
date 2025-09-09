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
    username = None
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='users/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Address(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='address_user')
    label = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.label} - {self.city}'

        
    