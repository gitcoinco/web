# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

import hashlib
import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Grant

# for outputing only the grants during the clr round
CLR_START_DATE = timezone.datetime(2019, 9, 15, 0, 0)
CLR_END_DATE = timezone.datetime(2019, 10, 2, 16, 0)
TZF = '%Y-%m-%dT%H:%M:%SZ'
anonymize = True


def do_anonymize(handle):
    if anonymize:
        handle = hashlib.sha224(handle.encode('utf-8')).hexdigest()
    return handle


class Command(BaseCommand):

    help = 'creates a dataset '

    def handle(self, *args, **options):
        # setup
        output = {
            'meta': {
                'clr_date_range':
                [
                    CLR_START_DATE.strftime(TZF),
                    CLR_END_DATE.strftime(TZF),
                ]
            },
            'grants': []

        }
        grants = Grant.objects.filter(active=True, network='mainnet')
        for grant in grants:
            grants_json = json.loads(grant.to_json_dict(fields=['pk', 'title'], properties=['url']))
            grants_json['tags'] = grant.tags
            grants_json['total_amount_received_usd_life'] = float(grant.amount_received)
            grants_json['admin_profile_name'] = do_anonymize(grant.admin_profile.handle)
            grants_json['admin_address'] = grant.contract_owner_address
            grants_json['logo'] = grant.logo.url if grant.logo else None
            grants_json['team'] = [do_anonymize(ele.handle) for ele in grant.team_members.all()]
            grants_json['contributions'] = []
            for sub in grant.subscriptions.all():
                for contrib in sub.subscription_contribution.filter(created_on__gt=CLR_START_DATE, created_on__lt=CLR_END_DATE):
                    contrib_json = json.loads(contrib.to_json_dict(fields=['pk', 'tx_id'], properties=[]))
                    contrib_json['created'] = contrib.created_on.strftime(TZF)
                    contrib_json['value_usd'] = float(contrib.subscription.amount_per_period_usdt)
                    contrib_json['profile'] = do_anonymize(contrib.subscription.contributor_profile.handle)
                    if not anonymize:
                        contrib_json['avatar'] = f"/dynamic/avatar/{contrib_json['profile']}"
                    contrib_json['pk'] = 'c-' + str(contrib.pk)
                    grants_json['contributions'].append(contrib_json)
            for pf in grant.phantom_funding.filter(created_on__gt=CLR_START_DATE, created_on__lt=CLR_END_DATE):
                contrib_json = json.loads(pf.to_json_dict(fields=['pk'], properties=[]))
                contrib_json['created'] = pf.created_on.strftime(TZF)
                contrib_json['profile'] = do_anonymize(pf.profile.handle)
                if not anonymize:
                    contrib_json['avatar'] = f"/dynamic/avatar/{contrib_json['profile']}"
                contrib_json['pk'] = 'v-' + str(pf.pk)
                contrib_json['tx_id'] = 'N/A'
                contrib_json['value_usd'] = pf.value
                grants_json['contributions'].append(contrib_json)

            output['grants'].append(grants_json)


        print(json.dumps(output))
