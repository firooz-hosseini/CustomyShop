from django.contrib import admin

def is_superadmin(user):
    return user.groups.filter(name="SuperAdmin").exists() or user.is_superuser

def is_admin(user):
    return user.groups.filter(name="Admin").exists()

def is_seller(user):
    return user.groups.filter(name="Seller").exists()

