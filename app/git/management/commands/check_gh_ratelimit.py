"""Check the Github ratelimit for the Gitcoin bot.

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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

from git.utils import get_current_ratelimit

warnings.filterwarnings('ignore', category=DeprecationWarning)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

GH_TOKEN = settings.GITHUB_API_TOKEN or None
CORE_LIMIT_THRESHOLD = 500  # Core GH API limit is 5000 requests per hour.
GRAPHQL_LIMIT_THRESHOLD = 500  # GraphQL GH limit is 5000 requests per hour.
SEARCH_LIMIT_THRESHOLD = 5  # Search GH limit is 30 requests per hour.


class Command(BaseCommand):

    help = 'check the current Github ratelimit'

    def handle(self, *args, **options):
        ratelimit = get_current_ratelimit(GH_TOKEN)

        if not ratelimit:
            logger.warning('Failed to fetch the Github ratelimit!')
            return

        core_remaining = ratelimit.core.remaining
        graphql_remaining = ratelimit.graphql.remaining
        search_remaining = ratelimit.search.remaining

        if core_remaining <= CORE_LIMIT_THRESHOLD:
            logger.warning('Core GH ratelimit breaching threshold!')
        print('Core GH ratelimit is: ', core_remaining)

        if graphql_remaining <= GRAPHQL_LIMIT_THRESHOLD:
            logger.warning('GraphQL GH ratelimit breaching threshold!')
        print('GraphQL GH ratelimit is: ', graphql_remaining)

        if search_remaining <= SEARCH_LIMIT_THRESHOLD:
            logger.warning('Search GH ratelimit breaching threshold!')
        print('Search GH ratelimit is: ', search_remaining)
