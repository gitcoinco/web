# -*- coding: utf-8 -*-
"""Define the Account authentication logic.

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
from social.backends.github import GithubOAuth2 as SocialGithubOAuth2


class GithubOAuth2(SocialGithubOAuth2):
    """The GitHub OAuth2 backend that adds scope if requested."""

    PUBLIC_REPO_SCOPE = 'public_repo'
    PRIVATE_REPO_SCOPE = 'repo'
    READ_ORG_SCOPE = 'read:org'

    EXTRA_DATA = [('scope', 'scope'), ] + SocialGithubOAuth2.EXTRA_DATA

    def get_scope(self):
        """Override get_scope to check for custom scope requirements."""
        scope = super(GithubOAuth2, self).get_scope()
        if self.data.get('private_repos'):
            scope = scope + [self.PRIVATE_REPO_SCOPE]
        elif self.data.get('public_repos'):
            scope = scope + [self.PUBLIC_REPO_SCOPE]
        if self.data.get('organization'):
            scope = scope + [self.READ_ORG_SCOPE]
        return scope

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        """
        Checks if the user has enabled private repos and, if so, ensures that their
        private repo access token isn't overridden.
        """
        data = super(GithubOAuth2, self).extra_data(user, uid, response, details=details, *args, **kwargs)

        social_auth = user.social_auth.filter(provider=self.name).first()
        additional_scope = self._check_additional_scope(social_auth)
        if additional_scope.get(READ_ORG_SCOPE):
            pass

        if self._has_additional_scope(social_auth):
            data['access_token'] = social_auth.extra_data.get('access_token')
            data['scope'] = data['scope'].replace(self.PUBLIC_REPO_SCOPE, self.PRIVATE_REPO_SCOPE)
        return data

    def _has_private_repos_enabled(self, social_auth):
        if social_auth and social_auth.extra_data:
            current_scopes = social_auth.extra_data.get('scope', '').split(',')
            return self.PRIVATE_REPO_SCOPE in current_scopes
        return False

    def _check_additional_scope(self, social_auth):
        """Check whether or not additional scope exists."""
        if social_auth and social_auth.extra_data:
            _scopes = social_auth.extra_data.get('scope', '').split(',')
            scope_dict = {
                'private_repos': self.PRIVATE_REPO_SCOPE in _scopes,
                'public_repos': self.PUBLIC_REPO_SCOPE in _scopes,
                'organizations': self.READ_ORG_SCOPE in _scopes,
            }
            scope_dict['has_additional_scope'] = all(x is False for x in scope_dict.values())
        return {}

    def _has_organizations_enabled(self, social_auth):
        if social_auth and social_auth.extra_data:
            current_scopes = social_auth.extra_data.get('scope', '').split(',')
            return self.PRIVATE_REPO_SCOPE in current_scopes
        return False
