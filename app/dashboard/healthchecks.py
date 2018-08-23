# -*- coding: utf-8 -*-
"""Define custom healthchecks.

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
from dashboard.utils import get_ipfs
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


class IPFSBackend(BaseHealthCheckBackend):
    """Define the IPFS healthcheck backend."""

    critical_service = True

    def check_status(self):
        """Define the functionality of the health check."""
        ipfs_connection = get_ipfs()
        if not ipfs_connection:
            raise HealthCheckException('IPFS Unreachable')

    def identifier(self):
        """Define the displayed name of the healthcheck."""
        return self.__class__.__name__
