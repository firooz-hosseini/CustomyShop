from django.contrib import admin
from .models import Product, ProductImage, Category, Comment, Rating


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image',)
    readonly_fields = ()
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'is_active')
    list_filter = ('id','category', 'is_active')
    search_fields = ('id', 'name',)
    ordering = ('id', 'name',)
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'is_active')
    list_filter = ('id', 'is_active',)
    search_fields = ('id', 'name',)
    ordering = ('id', 'name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'description', 'is_approved')
    list_filter = ('id', 'is_approved',)
    search_fields = ('id', 'user__email', 'product__name', 'description')
    ordering = ('id', '-created_at',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating')
    list_filter = ('id', 'rating',)
    search_fields = ('id', 'user__email', 'product__name')
    ordering = ('id', '-created_at',)