# -*- coding: utf-8 -*-
"""Define custom log filters for Gitcoin logging.

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
import logging
import socket


class HostFilter(logging.Filter):
    """Define the logging filter to add the current hostname to log output."""

    hostname = socket.gethostname()

    def filter(self, record):
        """Add the HostFilter derived hostname to log output."""
        record.hostname = HostFilter.hostname
        return True
