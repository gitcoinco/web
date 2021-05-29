# -*- coding: utf-8 -*-
"""Define the Healthcheck application configuration.

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
from __future__ import unicode_literals

from django.apps import AppConfig

from health_check.plugins import plugin_dir


class HealthcheckConfig(AppConfig):
    """Define the Healthcheck application configuration."""

    name = 'healthcheck'
    verbose_name = 'Healthcheck'

    def ready(self):
        """Handle signals on ready."""
        from healthcheck.healthchecks import DefaultIPFSBackend, GithubRateLimiting, InfuraIPFSBackend
        plugin_dir.register(InfuraIPFSBackend)
        plugin_dir.register(DefaultIPFSBackend)
        plugin_dir.register(GithubRateLimiting)
