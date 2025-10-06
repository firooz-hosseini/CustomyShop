from django.apps import AppConfig
from django.contrib import admin


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from .models import SiteConfiguration

        config = SiteConfiguration.get_solo()
        admin.site.site_header = config.site_header
        admin.site.site_title = config.site_title
        admin.site.index_title = config.index_title
