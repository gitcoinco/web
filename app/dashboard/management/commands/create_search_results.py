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

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Profile, HackathonEvent
from grants.models import Grant
from quests.models import Quest
from kudos.models import Token
from search.models import SearchResult
from app.sitemaps import StaticViewSitemap
from django.urls import reverse
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from search.models import SearchResult, ProgrammingLanguage, Page
import requests
from retail.utils import strip_html
class Command(BaseCommand):

    help = 'creates earnings records for deploy of https://github.com/gitcoinco/web/pull/5093'

    def handle(self, *args, **options):

        # regular URLs
        svs = StaticViewSitemap()
        for item in svs.items():
            try:
                uri = reverse(item)
                url = f"{settings.BASE_URL}{uri}".replace(f"/{uri}", f"{uri}")

                html_response = requests.get(url)
                soup = BeautifulSoup(html_response.text, 'html.parser')
                title = soup.findAll("title")[0].text
                try:
                    description = soup.findAll("meta", {"name": 'description'})[0].text
                except:
                    description = ''
                valid_title ='Grow Open Source' not in title and 'GitHub' not in title
                title = title if valid_title else item.capitalize() + " Page"
                print(title, item, url)
                obj, created = Page.objects.update_or_create(
                    key=item,
                    defaults={
                        "title":title,
                        "description":description,
                    }
                )
                SearchResult.objects.update_or_create(
                    source_type=ContentType.objects.get(app_label='search', model='page'),
                    source_id=obj.pk,
                    defaults={
                        "title":title,
                        "description":description,
                        "url":url,
                        "visible_to":None,
                    }
                    )
            except Exception as e:
                print(item, e)


        # prog languages
        from retail.utils import programming_languages_full
        for pl in programming_languages_full:
            obj, created = ProgrammingLanguage.objects.update_or_create(val=pl)
            urls = [f"/explorer?q={pl}", f"/users?q={pl}"]
            for url in urls:
                title = f"View {pl} Bounties"
                if 'users' in url:
                    title = f"View {pl} Coders"
                description = title
                SearchResult.objects.update_or_create(
                    source_type=ContentType.objects.get(app_label='search', model='programminglanguage'),
                    source_id=obj.pk,
                    title=title,
                    defaults={
                        "description":description,
                        "url":url,
                        "visible_to":None,
                    }
                    )
        # objects
        qses = [
            Grant.objects.all(),
            Token.objects.all(),
            Bounty.objects.current(),
            Quest.objects.filter(visible=True),
            Profile.objects.filter(hide_profile=False),
            HackathonEvent.objects.all(),
        ]
        for qs in qses:
            print(qs)
            for obj in qs:
                print(obj.pk)
                obj.save()

