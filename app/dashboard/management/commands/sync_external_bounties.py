'''
    Copyright (C) 2017 Gitcoin Core

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
import re
import warnings
import requests
import markdown
from urllib.parse import urlparse as parse
from urlextract import URLExtract
from lxml import etree

from django.core.management.base import BaseCommand

from github.utils import get_issues
from dashboard.models import ExternalBounty
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", category=DeprecationWarning)

logger = logging.getLogger(__name__)

extractor = URLExtract()


class Command(BaseCommand):

    help = 'get external bounties'

    def add_arguments(self, parser):
        parser.add_argument(
            '-source_github_url', '--source_github_url',
            action='store_true',
            dest='source_github_url',
            default='https://github.com/JGcarv/ethereum-bounty-hunters',
            help='Source Github url that contains the external bounties'
        )

        parser.add_argument('source_github_url')

    def handle(self, *args, **options):

        source_gh_url = 'https://github.com/JGcarv/ethereum-bounty-hunters'
        uri = parse(source_gh_url).path
        uri_array = uri.split('/')
        username = uri_array[1]
        repo = uri_array[2]

        gh_issues = get_issues(username,repo)

        for gh_issue in gh_issues:
            eb = ExternalBounty.objects.create(
                title=gh_issue.get('title'),
                url=gh_issue.get('html_url'),
                description=markdown.markdown(gh_issue.get('body')),
                amount=0.00,
                amount_denomination='USD',
                created_on=gh_issue.get('created_at'),

            )
            mkd_text = markdown.markdown(gh_issue.get('body'))
            #print(mkd_text)
            soup = BeautifulSoup(mkd_text, "lxml")
            for link in soup.find_all('a'):
                print(link.get('href'))

            #for url in urls:
            #    content = requests.get(url).content
