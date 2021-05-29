# -*- coding: utf-8
"""Define the application WSGI.

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
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

if os.environ.get('ENV') in ['prod', 'stage']:
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    application = Sentry(get_wsgi_application())
else:
    from dj_static import Cling
    application = Cling(get_wsgi_application())
