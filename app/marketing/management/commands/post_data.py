# -*- coding: utf-8 -*-
"""Define the GDPR reconsent command for EU users.

Copyright (C) 2020 Gitcoin Core

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
import time
import warnings
from datetime import datetime

from django.core.management.base import BaseCommand
import operator

from django.utils import timezone

from grants.models import *
from grants.models import CartActivity, Contribution, PhantomFunding
from grants.views import clr_round, next_round_start, round_end
from dashboard.models import Activity, Profile
from townsquare.models import Comment

text = ''

def pprint(_text, _text2=None):
    global text

    _text = str(_text)
    if _text2:
        _text += ", " + str(_text2)

    text += _text + "\n"
    print(_text)

warnings.filterwarnings("ignore", category=DeprecationWarning)

def do_post(text, comment=None):
    profile = Profile.objects.filter(handle='gitcoinbot').first()
    metadata = {
        'title': text,
    }
    activity = Activity.objects.create(profile=profile, activity_type='status_update', metadata=metadata)
    if comment:
        Comment.objects.create(
            profile=profile,
            activity=activity,
            comment=comment)

def grants():
    from grants.views import clr_active, clr_round
    if not clr_active:
        return

    ############################################################################3
    # total stats
    ############################################################################3

    start = next_round_start
    end = round_end
    day = (datetime.now() - start).days
    pprint("")
    pprint("================================")
    pprint(f"== BEEP BOOP BOP ⚡️          ")
    pprint(f"== Grants Round {clr_round} ({start.strftime('%m/%d/%Y')} ➡️ {end.strftime('%m/%d/%Y')})")
    pprint(f"== Day {day} Stats 💰🌲👇 ")
    pprint("================================")
    pprint("")

    must_be_successful = True

    contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end)
    if must_be_successful:
        contributions = contributions.filter(success=True)
    pfs = PhantomFunding.objects.filter(created_on__gt=start, created_on__lt=end)
    total = contributions.count() + pfs.count()

    current_carts = CartActivity.objects.filter(latest=True)
    num_carts = 0
    amount_in_carts = {}
    for ca in current_carts:
        for item in ca.metadata:
            currency, amount = item['grant_donation_currency'], item['grant_donation_amount']
            if currency not in amount_in_carts.keys():
                amount_in_carts[currency] = 0
            if amount:
                amount_in_carts[currency] += float(amount)

    contributors = len(set(list(contributions.values_list('subscription__contributor_profile', flat=True)) + list(pfs.values_list('profile', flat=True))))
    amount = sum([float(contrib.subscription.amount_per_period_usdt) for contrib in contributions] + [float(pf.value) for pf in pfs])

    pprint(f"Contributions: {total}")
    pprint(f"Contributors: {contributors}")
    pprint(f'Amount Raised: ${round(amount, 2)}')
    pprint(f"In carts, but not yet checked out yet:")
    for key, val in amount_in_carts.items():
        pprint(f"- {round(val, 2)} {key}")

    ############################################################################3
    # top contributors
    ############################################################################3

    all_contributors_by_amount = {}
    all_contributors_by_num = {}
    for contrib in contributions:
        key = contrib.subscription.contributor_profile.handle
        if key not in all_contributors_by_amount.keys():
            all_contributors_by_amount[key] = 0
            all_contributors_by_num[key] = 0

        all_contributors_by_num[key] += 1
        all_contributors_by_amount[key] += contrib.subscription.amount_per_period_usdt

    all_contributors_by_num = sorted(all_contributors_by_num.items(), key=operator.itemgetter(1))
    all_contributors_by_amount = sorted(all_contributors_by_amount.items(), key=operator.itemgetter(1))
    all_contributors_by_num.reverse()
    all_contributors_by_amount.reverse()

    pprint("")
    pprint("=======================")
    pprint("")

    limit = 25
    pprint(f"Top Contributors by Num Contributions (Round {clr_round})")
    counter = 0
    for obj in all_contributors_by_num[0:limit]:
        counter += 1
        pprint(f"{counter} - {str(round(obj[1]))} by @{obj[0]}")

    pprint("")
    pprint("=======================")
    pprint("")

    counter = 0
    pprint(f"Top Contributors by Amount of Contributions (Round {clr_round})")
    for obj in all_contributors_by_amount[0:limit]:
        counter += 1
        pprint(f"{counter} - ${str(round(obj[1], 2))} by @{obj[0]}")



    ############################################################################3
    # new feature stats for round {clr_round} 
    ############################################################################3

    subs_stats = False
    if subs_stats:
        subs = Subscription.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=48))
        subs = subs.filter(subscription_contribution__success=True)
        pprint(subs.count())
        pprint(subs.filter(num_tx_approved__gt=1).count())
        pprint(subs.filter(is_postive_vote=False).count())


    ############################################################################3
    # all contributions export
    ############################################################################3

    start = next_round_start
    end = round_end
    export = False
    if export:
        contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True, subscription__network='mainnet')[0:100]
        pprint("tx_id1, tx_id2, from address, amount, amount_minus_gitcoin, token_address")
        for contribution in contributions:
            pprint(contribution.tx_id, 
                contribution.split_tx_id,
                contribution.subscription.contributor_address,
                contribution.subscription.amount_per_period, 
                contribution.subscription.amount_per_period_minus_gas_price,
                contribution.subscription.token_address)

    pprint("")
    pprint("=======================")
    pprint("More @")
    pprint("⌗ https://gitcoin.co/grants/activity")
    pprint("⌗ https://gitcoin.co/grants/stats")
    pprint("=======================")

    global text
    do_post(text)
class Command(BaseCommand):

    help = 'puts grants stats on town suqare'

    def add_arguments(self, parser):
        parser.add_argument('what', 
            default='',
            type=str,
            help="what to post"
            )

    def handle(self, *args, **options):
        if options['what'] == 'grants':
            grants()
        else:
            print('option not found')




