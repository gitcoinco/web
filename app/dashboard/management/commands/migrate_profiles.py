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

from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.helpers import record_bounty_activity
from dashboard.models import Bounty, Profile, Tip
from dashboard.tip_views import record_tip_activity


class Command(BaseCommand):

    help = 'runs all mgmt commands for https://github.com/gitcoinco/web/pull/5093'

    def handle(self, *args, **options):


        bounties = Bounty.objects.current().filter(web3_created__lt=timezone.datetime(2019,3,5)).filter(network='mainnet')
        for bounty in bounties:
            try:
                record_bounty_activity('new_bounty', None, bounty, _fulfillment=None, override_created=bounty.web3_created)
                #print(bounty.url)
                for ful in bounty.fulfillments.all():
                    record_bounty_activity('work_submitted', None, bounty, _fulfillment=ful, override_created=ful.created_on)
            except Exception as e:
                print(e)


        for tip in Tip.objects.filter(network='mainnet').filter(created_on__lt=timezone.datetime(2019,3,5)):
            try:
                record_tip_activity(tip, tip.username, 'new_tip', override_created=tip.created_on)
                #print(tip.pk)
            except Exception as e:
                print(e)


        for instance in Profile.objects.filter(hide_profile=False):
            instance.calculate_all()
            instance.save()
