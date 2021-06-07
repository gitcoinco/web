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

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import BountyFulfillment, Profile, Tip
from grants.models import Contribution
from kudos.models import KudosTransfer


class Command(BaseCommand):

    help = 'creates earnings records for deploy of https://github.com/gitcoinco/web/pull/5093'

    def handle(self, *args, **options):
        for obj in BountyFulfillment.objects.all():
            obj.save()
        for obj in Tip.objects.all():
            obj.save()
        for obj in Contribution.objects.all():
            obj.save()
        for obj in KudosTransfer.objects.all():
            obj.save()
        for obj in Profile.objects.all():
            obj.save()
