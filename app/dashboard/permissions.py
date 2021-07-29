# -*- coding: utf-8 -*-
"""Define dashboard specific DRF API routes.

Copyright (C) 2021 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from rest_framework import permissions
from townsquare.utils import can_pin


class CanPinPost(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        what = request.data.get('what', False)
        if not what:
            return True # pass control to view validation
        return can_pin(request, what)


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
