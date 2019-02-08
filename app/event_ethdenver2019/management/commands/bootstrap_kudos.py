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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from kudos.models import BulkTransferCoupon, Token


class Command(BaseCommand):

    help = 'bootstraps the kudos data on the platform'

    def handle(self, *args, **options):

        trophy_kudos = Token.objects.filter(name__contains='ethdenver_winner')
        plaque_kudos = Token.objects.filter(Q(name__contains='_ethdenver_2019') | Q(name__contains='be_a_bufficorn'))
        all_kudos = plaque_kudos + trophy_kudos

        
        print(f"got {trophy_kudos.count()} trophies")
        print(f"got {plaque_kudos.count()} plaques")
