from django.contrib import admin
from .models import Store, StoreItem, SellerRequest
from django.utils import timezone


class StoreItemInline(admin.TabularInline):
    model = StoreItem
    extra = 0
    fields = ('id', 'product', 'stock', 'price', 'discount_price', 'is_active')
    readonly_fields = ()
    show_change_link = True


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'seller', 'description')
    list_filter = ('id', 'seller',)
    search_fields = ('id', 'name', 'seller__email')
    ordering = ('-id', 'name',)
    inlines = [StoreItemInline]
    

@admin.action(description="Enable selected store items")
def enable_store_items(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Disable selected store items")
def disable_store_items(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'store', 'stock', 'price', 'discount_price', 'is_active')
    list_filter = ('id', 'store', 'is_active')
    search_fields = ('id', 'product__name', 'store__name')
    ordering = ('id', 'store', 'product',)
    actions = [enable_store_items, disable_store_items]

@admin.register(SellerRequest)
class SellerRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'reviewed_at')
    list_filter = ('id', 'status',)
    search_fields = ('id', 'user__email',)
    ordering = ('id', '-reviewed_at',)

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

    approve_request.short_description = "Approve selected requests"

    def reject_request(self, request, queryset):
        for req in queryset:
            if req.status != SellerRequest.PENDING:
                continue
            req.status = SellerRequest.REJECTED
            req.reviewed_at = timezone.now()
            req.save()

    reject_request.short_description = "Reject selected requests"


