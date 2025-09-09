from django.db import models
from core.models import BaseModel
from accounts.models import CustomUser ,Address

class Store(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='store_address')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_seller')




