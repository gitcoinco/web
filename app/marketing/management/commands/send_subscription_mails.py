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
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests
from dashboard.models import Bounty, Subscription
from marketing.mails import new_bounty


class Command(BaseCommand):

    help = 'pulls mailchimp emails'

    def handle(self, *args, **options):

        for sub in Subscription.objects.all():
            url = "https://gitcoin.co/" + sub.raw_data
            bounties_pks = [b['pk'] for b in requests.get(url).json()]
            for bounty in Bounty.objects.filter(pk__in=bounties_pks, idx_status='open'):
                if bounty.web3_created > (timezone.now() - timezone.timedelta(hours=24)):
                    new_bounty(bounty, to_emails=[sub.email])
