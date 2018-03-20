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
import warnings
import markdown
from urllib.parse import urlparse as parse
from urlextract import URLExtract
import locale


from django.core.management.base import BaseCommand

from github.utils import get_issues
from dashboard.models import ExternalBounty
from bs4 import BeautifulSoup
import spacy
from textacy import doc as textacy_doc
from textacy import extract as text_extract

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
        nlp = spacy.load('en_core_web_sm')
        source_gh_url = 'https://github.com/JGcarv/ethereum-bounty-hunters'
        uri = parse(source_gh_url).path
        uri_array = uri.split('/')
        username = uri_array[1]
        repo = uri_array[2]

        gh_issues = get_issues(username,repo)

        for gh_issue in gh_issues:

            mkd_text = markdown.markdown(gh_issue.get('body'))
            soup = BeautifulSoup(mkd_text, "lxml")
            just_text = ''.join(soup.findAll(text=True))
            print(just_text)
            doc = nlp(just_text)
            textacy_parsed_doc = textacy_doc.Doc(doc)

            named_enties = list(text_extract.named_entities(textacy_parsed_doc, include_types=['MONEY']))
            for named_entity in named_enties:
                print('named entity for bounty amount {0}'.format(named_entity.text))
            if len(named_enties) == 0:
                last_entity = 0
            elif len(named_enties) == 1:
                last_entity = named_enties[0]
            else:
                last_entity = named_enties[-1:]
            print(last_entity.text)
            eurs = text_extract.semistructured_statements(textacy_parsed_doc, "EUR")

            for eur in list(eurs):
                print('eur for bounty amount {0}'.format(eur.text))

            eb = ExternalBounty.objects.create(
                title=gh_issue.get('title'),
                url=gh_issue.get('html_url'),
                description=markdown.markdown(gh_issue.get('body')),
                amount=int(last_entity.text),
                amount_denomination='USD',
                created_on=gh_issue.get('created_at'),

            )

            print('---------------------')

