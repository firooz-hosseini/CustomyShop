from django.contrib import admin
from django.utils import timezone

from accounts.admin_utils import is_admin, is_seller, is_superadmin

from .models import SellerRequest, Store, StoreItem


class StoreItemInline(admin.TabularInline):
    model = StoreItem
    extra = 0
    fields = ('id', 'product', 'stock', 'price', 'discount_price', 'is_active')
    readonly_fields = ()
    show_change_link = True


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'seller', 'description')
    list_filter = (
        'id',
        'seller',
    )
    search_fields = ('id', 'name', 'seller__email')
    ordering = (
        '-id',
        'name',
    )
    inlines = [StoreItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_superadmin(request.user):
            return qs
        if is_seller(request.user):
            return qs.filter(store__seller=request.user)
        if is_admin(request.user):
            return qs.all()
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if is_superadmin(request.user):
            return True
        if is_seller(request.user) and obj:
            return obj.store.seller == request.user
        if is_admin(request.user):
            return False
        return False

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)


@admin.action(description='Enable selected store items')
def enable_store_items(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description='Disable selected store items')
def disable_store_items(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'store',
        'stock',
        'price',
        'discount_price',
        'is_active',
    )
    list_filter = ('id', 'store', 'is_active')
    search_fields = ('id', 'product__name', 'store__name')
    ordering = (
        'id',
        'store',
        'product',
    )
    actions = [enable_store_items, disable_store_items]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_superadmin(request.user):
            return qs
        if is_seller(request.user):
            return qs.filter(store__seller=request.user)
        if is_admin(request.user):
            return qs.all()
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if is_superadmin(request.user):
            return True

        if is_seller(request.user):
            if obj is None:
                return True
            return obj.store.seller == request.user

        if is_admin(request.user):
            return False
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        if is_superadmin(request.user):
            return True

        if is_seller(request.user):
            return True

        if is_admin(request.user):
            return False
        return False


@admin.register(SellerRequest)
class SellerRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'reviewed_at')
    list_filter = (
        'id',
        'status',
    )
    search_fields = (
        'id',
        'user__email',
    )
    ordering = (
        'id',
        '-reviewed_at',
    )

    actions = ['approve_request', 'reject_request']

    def approve_request(self, request, queryset):
        for req in queryset:
            if req.status != SellerRequest.PENDING:
                continue

            req.status = SellerRequest.APPROVED
            req.reviewed_at = timezone.now()
            req.save()

            user = req.user
            user.role = 'seller'
            user.is_seller = True
            user.save()

    approve_request.short_description = 'Approve selected requests'

    def reject_request(self, request, queryset):
        for req in queryset:
            if req.status != SellerRequest.PENDING:
                continue
            req.status = SellerRequest.REJECTED
            req.reviewed_at = timezone.now()
            req.save()

    reject_request.short_description = 'Reject selected requests'
