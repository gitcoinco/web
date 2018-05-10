from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow profile owners to edit it.
    """

    def has_profile_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
