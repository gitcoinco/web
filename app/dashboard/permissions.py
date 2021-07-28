from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.basename == 'activity':
            return obj.profile and obj.profile == request.user.profile \
                or obj.other_profile and obj.other_profile == request.user.other_profile
