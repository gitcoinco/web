'''
    Copyright (C) 2019 Gitcoin Core

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
import re

from django.core.management.base import BaseCommand

from dashboard.models import Bounty
from marketing.models import Keyword


class Command(BaseCommand):

    help = 'syncs autocomplete keywords'

    def handle(self, *args, **options):

        keywords = []

        for bounty in Bounty.objects.all():
            keywords.append(bounty.org_name)
            keywords.append(bounty.bounty_owner_github_username)
            for fulfiller in bounty.fulfillments.all():
                if fulfiller.fulfiller_github_username:
                    keywords.append(fulfiller.fulfiller_github_username)
            if bounty.keywords:
                for keyword in bounty.keywords_list:
                    keywords.append(keyword)
        Keyword.objects.all().delete()
        for keyword in set(keywords):
            if keyword:
                keyword = re.sub(r'\W+', '', keyword).lower()
                if keyword:
                    Keyword.objects.get_or_create(keyword=keyword)
                    print(keyword)
