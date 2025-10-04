from django.db import models
from django.utils import timezone


class BaseQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def restore(self):
        return super().update(is_deleted=False, deleted_at=None)


class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_objects(self):
        return BaseQuerySet(self.model, using=self._db)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

    def restore(self):
        return self.get_queryset().restore()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = BaseManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        super().delete()


class SiteConfiguration(models.Model):
    site_header = models.CharField(max_length=200, default='CustomyShop Admin')
    site_title = models.CharField(max_length=200, default='CustomyShop Portal')
    index_title = models.CharField(max_length=200, default='Dashboard')
    logo = models.FileField(upload_to='branding/', blank=True, null=True)
    footer_text = models.TextField(default='All rights reserved © CustomyShop Online Store')
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    email_subscription_text = models.CharField(
        max_length=255, default='Subscribe for latest news:'
    )
    contact_number = models.CharField(max_length=50, default='+98 917 411 6470')

    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'

    def __str__(self):
        return 'Site Configuration'

    @classmethod
    def get_solo(cls):
        # always return the single instance (create it if missing)
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
