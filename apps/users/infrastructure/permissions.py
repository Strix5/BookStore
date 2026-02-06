from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        owner = getattr(obj, "user", None)
        if owner:
            return owner.pk == getattr(request.user, "pk", None)
        return obj.pk == getattr(request.user, "pk", None)


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_author or request.user.is_staff
