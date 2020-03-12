'''
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

'''
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from dashboard.models import Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates the Chat DB"

    def handle(self, *args, **options):

        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE chat")

                row = cursor.fetchone()

            return row
        except Exception as e:
            logger.error(str(e))
