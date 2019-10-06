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

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import UserAction
from grants.models import Grant

# for outputing only the grants during the clr round
CLR_START_DATE = timezone.datetime(2019, 9, 15, 0, 0)
CLR_END_DATE = timezone.datetime(2019, 10, 2, 16, 0)
TZF = '%Y-%m-%dT%H:%M:%SZ'
anonymize = not settings.DEBUG
anonymize = True
output = 'data'

def profile_to_ip_address(profile, time):
    uas = UserAction.objects.filter(action='Visit', profile=profile)
    uas = uas.filter(created_on__gt=(time-timezone.timedelta(hours=1)))
    uas = uas.filter(created_on__lt=(time+timezone.timedelta(hours=1)))
    if uas.exists():
        return uas.first().ip_address


def do_anonymize(handle):
    if anonymize and handle:
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
        contrib_count = 0
        contributors = []
        grants = Grant.objects.filter(active=True, network='mainnet')
        for grant in grants:
            grants_json = json.loads(grant.to_json_dict(fields=['pk', 'title'], properties=['url']))
            grants_json['tags'] = grant.tags
            grants_json['total_amount_received_usd_life'] = float(grant.amount_received)
            grants_json['admin_profile_name'] = do_anonymize(grant.admin_profile.handle)
            grants_json['admin_address'] = grant.contract_owner_address
            try:
                grants_json['estimated_round_3_clr_match_usd'] = grant.clr_prediction_curve[0][1]
            except:
                grants_json['estimated_round_3_clr_match_usd'] = 0
            grants_json['logo'] = grant.logo.url if grant.logo else None
            grants_json['team'] = [do_anonymize(ele.handle) for ele in grant.team_members.all()]
            grants_json['contributions'] = []
            for sub in grant.subscriptions.all():
                for contrib in sub.subscription_contribution.filter(created_on__gt=CLR_START_DATE, created_on__lt=CLR_END_DATE):
                    contrib_json = json.loads(contrib.to_json_dict(fields=['pk', 'tx_id'], properties=[]))
                    contrib_json['created'] = contrib.created_on.strftime(TZF)
                    contrib_json['value_usd'] = float(contrib.subscription.amount_per_period_usdt)
                    contrib_json['contributor_profile_name'] = do_anonymize(contrib.subscription.contributor_profile.handle)
                    contrib_json['contributor_profile_created_on'] = contrib.subscription.contributor_profile.created_on.strftime(TZF)
                    contrib_json['ip_address'] = do_anonymize(profile_to_ip_address(contrib.subscription.contributor_profile, contrib.subscription.created_on))
                    contrib_json['num_tx_approved'] = int(contrib.subscription.num_tx_approved - 1)
                    if not anonymize:
                        contrib_json['avatar'] = f"/dynamic/avatar/{contrib_json['contributor_profile_name']}"
                    contrib_json['pk'] = 'c-' + str(contrib.pk)
                    grants_json['contributions'].append(contrib_json)
                    contrib_count+=1
                    contributors.append(contrib_json['contributor_profile_name'])
            for pf in grant.phantom_funding.filter(created_on__gt=CLR_START_DATE, created_on__lt=CLR_END_DATE):
                contrib_json = json.loads(pf.to_json_dict(fields=['pk'], properties=[]))
                contrib_json['created'] = pf.created_on.strftime(TZF)
                contrib_json['contributor_profile_name'] = do_anonymize(pf.profile.handle)
                contrib_json['contributor_profile_created_on'] = pf.profile.created_on.strftime(TZF)
                contrib_json['num_tx_approved'] = 1
                if not anonymize:
                    contrib_json['avatar'] = f"/dynamic/avatar/{contrib_json['contributor_profile_name']}"
                contrib_json['pk'] = 'v-' + str(pf.pk)
                contrib_json['tx_id'] = 'N/A'
                contrib_json['value_usd'] = pf.value
                contrib_json['ip_address'] = do_anonymize(profile_to_ip_address(pf.profile, pf.created_on))
                grants_json['contributions'].append(contrib_json)
                contrib_count+=1
                contributors.append(contrib_json['contributor_profile_name'])

            output['grants'].append(grants_json)

        if output == 'stats':
            print(f'contrib_count: {contrib_count}')
            print(f'contributors_count: {len(set(contributors))}')
        else:
            print(json.dumps(output))
