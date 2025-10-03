from django.contrib import admin

def is_superadmin(user):
    return user.groups.filter(name="SuperAdmin").exists() or user.is_superuser

def is_support(user):
    return user.groups.filter(name="SupportStaff").exists()

def is_seller(user):
    return user.groups.filter(name="Seller").exists()

def is_customer(user):
    return user.groups.filter(name="Customer").exists()
