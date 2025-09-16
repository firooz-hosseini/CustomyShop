from django.contrib import admin
from .models import Product, ProductImage, Category, Comment, Rating

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Rating)

