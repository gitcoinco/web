# -*- coding: utf-8 -*-
"""Define custom healthchecks.

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
from dashboard.utils import IPFSCantConnectException
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


class DefaultIPFSBackend(BaseHealthCheckBackend):
    """Define the IPFS healthcheck backend."""

    critical_service = True

    def check_status(self):
        """Define the functionality of the health check."""
        from dashboard.utils import get_ipfs
        try:
            ipfs_connection = get_ipfs()
        except IPFSCantConnectException:
            ipfs_connection = None

        if not ipfs_connection:
            raise HealthCheckException('Default IPFS Unreachable')

    def identifier(self):
        """Define the displayed name of the healthcheck."""
        return self.__class__.__name__


class InfuraIPFSBackend(BaseHealthCheckBackend):
    """Define the IPFS healthcheck backend."""

    critical_service = True

    def check_status(self):
        """Define the functionality of the health check."""
        from dashboard.utils import get_ipfs
        try:
            ipfs_connection = get_ipfs(host='ipfs.infura.io', port=5001)
        except IPFSCantConnectException:
            ipfs_connection = None

        if not ipfs_connection:
            raise HealthCheckException('Infura IPFS Unreachable')

    def identifier(self):
        """Define the displayed name of the healthcheck."""
        return self.__class__.__name__


class GithubRateLimiting(BaseHealthCheckBackend):
    """Define the Github ratelimiting healthcheck backend."""

    critical_service = True

    def check_status(self):
        """Define the functionality of the health check."""
        from git.utils import get_current_ratelimit
        gh_ratelimit = get_current_ratelimit()

        is_core_ok = gh_ratelimit.core.remaining >= 500  # Limit is 5000
        is_graphql_ok = gh_ratelimit.graphql.remaining >= 500  # Limit is 5000
        is_search_ok = gh_ratelimit.search.remaining >= 5  # Limit is 30

        if not is_core_ok or not is_graphql_ok or not is_search_ok:
            raise HealthCheckException('Github Ratelimiting Danger Zone')

    def identifier(self):
        """Define the displayed name of the healthcheck."""
        return self.__class__.__name__
