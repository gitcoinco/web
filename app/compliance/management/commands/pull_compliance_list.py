'''
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

'''

import urllib.request
import xml.etree as etree
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand
from django.db import transaction

from compliance.models import Country, Entity


def insert_countries():
    # clear existing table
    Country.objects.all().delete()

    # pull data
    countries = 'Balkans, Belarus, Burma, Cote D\'Ivoire , Cuba, Democratic Republic of Congo, Iran, Iraq, Liberia, North Korea, Sudan, Syria, Zimbabwe'.split(',')

    # insert data
    for country in countries:
        Country.objects.create(name=country)


def insert_entities():
    # clear existing table
    Entity.objects.all().delete()

    # pull data
    url = 'https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml'
    response = urllib.request.urlopen(url).read()
    tree = ET.fromstring(response)

    # insert data
    for ele in tree:
        try:
            response = {}
            keys = ['firstName', 'lastName', 'sdnType', 'city', 'country', 'program', 'stateOrProvince', 'uid']
            for key in keys:
                elements = ele.findall('{http://tempuri.org/sdnList.xsd}' + f'{key}')
                element = elements[0].text if len(elements) else ''
                response[key] = element
            response['fullName'] = (response.get('firstName', '') + ' ' + response.get('lastName', '')).strip()
            Entity.objects.create(**response)
        except Exception as e:
            print(e)


class Command(BaseCommand):

    help = 'syncs compliance info from remote server'

    def handle(self, *args, **options):
        with transaction.atomic():
            insert_countries()
            insert_entities()
