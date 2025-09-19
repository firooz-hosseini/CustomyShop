from django.contrib import admin
from .models import Store, StoreItem, SellerRequest
from django.utils import timezone
from accounts.models import CustomUser

admin.site.register(Store)
admin.site.register(StoreItem)


@admin.register(SellerRequest)
class SellerRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('user__email',)

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

    approve_request.short_description = "Approve selected requests and create store"

    def reject_request(self, request, queryset):
        for req in queryset:
            if req.status != SellerRequest.PENDING:
                continue
            req.status = SellerRequest.REJECTED
            req.reviewed_at = timezone.now()
            req.save()

    reject_request.short_description = "Reject selected requests"
