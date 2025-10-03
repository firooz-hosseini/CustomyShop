from django.contrib import admin

from accounts.admin_utils import is_seller, is_superadmin, is_support

from .models import Category, Comment, Product, ProductImage, Rating


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image',)
    readonly_fields = ()
    show_change_link = True


@admin.action(description='Enable selected products')
def enable_products(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description='Disable selected products')
def disable_products(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'is_active')
    list_filter = ('id', 'category', 'is_active')
    search_fields = (
        'id',
        'name',
    )
    ordering = (
        'id',
        'name',
    )
    inlines = [ProductImageInline]
    actions = [enable_products, disable_products]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_superadmin(request.user):
            return qs
        if is_seller(request.user):
            # Sellers see only their products through StoreItem
            return qs.filter(storeitem__store__owner=request.user).distinct()
        if is_support(request.user):
            return qs.none()  # SupportStaff cannot manage products
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if is_superadmin(request.user):
            return True
        if is_seller(request.user) and obj:
            return obj.storeitem_set.filter(store__owner=request.user).exists()
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        return is_superadmin(request.user) or is_seller(request.user)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'is_active')
    list_filter = (
        'id',
        'is_active',
    )
    search_fields = (
        'id',
        'name',
    )
    ordering = (
        'id',
        'name',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'description', 'is_approved')
    list_filter = (
        'id',
        'is_approved',
    )
    search_fields = ('id', 'user__email', 'product__name', 'description')
    ordering = (
        'id',
        '-created_at',
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating')
    list_filter = (
        'id',
        'rating',
    )
    search_fields = ('id', 'user__email', 'product__name')
    ordering = (
        'id',
        '-created_at',
    )
