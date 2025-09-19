# stores/permissions.py

from rest_framework import permissions
from .models import SellerRequest

class IsOwnerOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user
