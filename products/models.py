from django.db import models
from core.models import BaseModel
from accounts.models import CustomUser

class Product(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='product_category')
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name

class Category(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='categories/')
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

class ProductImage(BaseModel):
    image = models.ImageField(upload_to='products/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='             image_product')


class Comment(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comment_product')
    text = models.TextField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'User: {self.user.first_name}, Product: {self.product.name}, Text: {self.text}'
    


class Rating(BaseModel):
    scores = [(1, 'very bad'), (2, 'bad'), (3, 'normal'),(4, 'good'),(5, 'very good')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rating_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rating_product')
    rating = models.PositiveIntegerField(choices=scores)


    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'User: {self.user.first_name}, Product: {self.product.name}, rating: {self.rating}'
    





