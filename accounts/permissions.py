from rest_framework import permissions

class IsOwnerOrStore(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        
        if obj.store and hasattr(request.user, 'store') and obj.store == request.user.store:
            return True
        
        return False