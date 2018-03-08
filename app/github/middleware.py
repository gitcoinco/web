# -*- coding: utf-8 -*-
"""Handle Github middleware.

Copyright (C) 2018 Gitcoin Core

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
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

from dashboard.models import Profile
from github.utils import is_github_token_valid


class GithubAuthMiddleware(MiddlewareMixin):
    """Handle checking validity of Github OAuth tokens."""

    def process_response(self, request, response):
        """Perform the check on request."""
        token = request.session.get('access_token')
        expiration = request.session.get('access_token_last_validated')
        handle = request.session.get('handle')

        if token and handle:
            is_valid = is_github_token_valid(token, expiration)
            if is_valid:
                request.session['access_token_last_validated'] = now().isoformat()
            else:
                request.session.pop('access_token', '')
                request.session.pop('handle', '')
                request.session.pop('access_token_last_validated', '')
                profile = Profile.objects.filter(handle=handle).first()
                profile.github_access_token = ''
                profile.save()
            request.session.modified = True
        return response
