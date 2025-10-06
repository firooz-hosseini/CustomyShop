from django.contrib import admin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("General", {"fields": ("site_header", "site_title", "index_title", "logo")}),
        ("Footer", {"fields": ("footer_text", "contact_number")}),
        ("Social Links", {"fields": ("instagram", "facebook", "youtube")}),
        ("Newsletter", {"fields": ("email_subscription_text",)}),
    )

    def has_add_permission(self, request):
        # only allow one configuration instance
        return not SiteConfiguration.objects.exists()