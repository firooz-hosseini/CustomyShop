from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import CustomUser
from products.models import Product, Category, Comment, Rating
from stores.models import Store, StoreItem
from orders.models import Order, OrderItem, Payment, Cart, CartItem

class Command(BaseCommand):
    help = "Create default user groups and assign permissions"

    def handle(self, *args, **options):
        # Define groups
        groups = ["SuperAdmin", "SupportStaff", "Seller", "Customer"]

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' created"))
            else:
                self.stdout.write(self.style.WARNING(f"Group '{group_name}' already exists"))

        # Permissions
        # SuperAdmin: all permissions
        super_admin_group = Group.objects.get(name="SuperAdmin")
        super_admin_group.permissions.set(Permission.objects.all())
        self.stdout.write(self.style.SUCCESS("Assigned all permissions to SuperAdmin"))

        # SupportStaff: manage Orders, OrderItems, Payments, Cart, CartItem
        support_group = Group.objects.get(name="SupportStaff")
        support_permissions = []
        models = [Order, OrderItem, Payment, Cart, CartItem]
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=content_type)
            support_permissions.extend(perms)
        support_group.permissions.set(support_permissions)
        self.stdout.write(self.style.SUCCESS("Assigned order/payment permissions to SupportStaff"))

        # Seller: manage only their StoreItem
        seller_group = Group.objects.get(name="Seller")
        seller_permissions = []
        content_type = ContentType.objects.get_for_model(StoreItem)
        perms = Permission.objects.filter(content_type=content_type)
        seller_permissions.extend(perms)
        seller_group.permissions.set(seller_permissions)
        self.stdout.write(self.style.SUCCESS("Assigned store item permissions to Seller"))

        # Customer: no admin access
        customer_group = Group.objects.get(name="Customer")
        customer_group.permissions.clear()
        self.stdout.write(self.style.SUCCESS("Cleared permissions for Customer"))

        self.stdout.write(self.style.SUCCESS("All groups and permissions configured successfully"))
