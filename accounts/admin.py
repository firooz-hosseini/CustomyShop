from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .admin_utils import is_superadmin
from .models import Address, CustomUser


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = (
        'id',
        'label',
        'address_line_1',
        'address_line_2',
        'city',
        'postal_code',
        'country',
        'is_default',
    )
    readonly_fields = ()
    show_change_link = True


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ['id', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    ordering = ['-id']
    inlines = [AddressInline]

    fieldsets = (
        (None, {'fields': ('email', 'password', 'image')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_staff',
                    'is_active',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
            },
        ),
    )
    readonly_fields = ['last_login', 'date_joined']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only SuperAdmin can see all users
        if is_superadmin(request.user):
            return qs
        # Others cannot access users
        return qs.none()

    def has_change_permission(self, request, obj=None):
        return is_superadmin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_superadmin(request.user)

    def has_add_permission(self, request):
        return is_superadmin(request.user)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'store',
        'label',
        'address_line_1',
        'address_line_2',
        'city',
        'postal_code',
        'country',
        'is_default',
    )
    list_filter = ('city', 'country', 'is_default')
    search_fields = (
        'id',
        'user__email',
        'address_line_1',
        'city',
        'postal_code',
        'label',
    )
    ordering = (
        'id',
        'user',
    )
