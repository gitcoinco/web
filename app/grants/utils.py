# -*- coding: utf-8 -*-
"""Define the Grant utilities.

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
import logging
import os
from decimal import Decimal
from random import randint, seed
from secrets import token_hex

from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate
from perftools.models import JSONStore

logger = logging.getLogger(__name__)

block_codes = ('▖', '▗', '▘', '▙', '▚', '▛', '▜', '▝', '▞', '▟')
emoji_codes = ('🎉', '🎈', '🎁', '🎊', '🙌', '🥂', '🎆', '🔥', '⚡', '👍')


def get_upload_filename(instance, filename):
    salt = token_hex(16)
    file_path = os.path.basename(filename)
    return f"grants/{getattr(instance, '_path', '')}/{salt}/{file_path}"


def get_leaderboard():
    return JSONStore.objects.filter(view='grants', key='leaderboard').order_by('-pk').first().data


def generate_leaderboard(max_items=100):
    from grants.models import Subscription, Contribution
    handles = Subscription.objects.all().values_list('contributor_profile__handle', flat=True)
    default_dict = {
        'rank': None,
        'no': 0,
        'sum': 0,
        'handle': None,
    }
    users_to_results = { ele : default_dict.copy() for ele in handles }

    # get all contribution attributes
    for contribution in Contribution.objects.all().select_related('subscription'):
        key = contribution.subscription.contributor_profile.handle
        users_to_results[key]['handle'] = key
        amount = contribution.subscription.get_converted_amount(False)
        if amount:
            users_to_results[key]['no'] += 1
            users_to_results[key]['sum'] += round(amount)
    # prepare response for view
    items = []
    counter = 1
    for item in sorted(users_to_results.items(), key=lambda kv: kv[1]['sum'], reverse=True):
        item = item[1]
        if item['no']:
            item['rank'] = counter
            items.append(item)
            counter += 1
    return items[:max_items]


def is_grant_team_member(grant, profile):
    """Checks to see if profile is a grant team member

    Args:
        grant (grants.models.Grant): The grant in question.
        profile (dashboard.models.Profile): The current user's profile.

    """
    if not profile:
        return False
    is_team_member = False
    if grant.admin_profile == profile:
        is_team_member = True
    else:
        for team_member in grant.team_members.all():
            if team_member.id == profile.id:
                is_team_member = True
                break
    return is_team_member

def amount_in_wei(tokenAddress, amount):
    from dashboard.tokens import addr_to_token
    token = addr_to_token(tokenAddress)
    decimals = token['decimals'] if token else 18
    return float(amount) * 10**decimals

def which_clr_round(timestamp):
    import datetime, pytz
    utc = pytz.UTC

    date_ranges = {
        1: [(2019, 2, 1), (2019, 2, 15)],   # Round 1: 2/1/2019 – 2/15/2019
        2: [(2019, 3, 5), (2019, 4, 19)],   # Round 2: 3/5/2019 - 4/19/2019
        3: [(2019, 9, 16), (2019, 9, 30)],  # Round 3: 9/16/2019 - 9/30/2019
        4: [(2020, 1, 6), (2020, 1, 21)],   # Round 4: 1/6/2020 — 1/21/2020
        5: [(2020, 3, 23), (2020, 4, 7)],   # Round 5: 3/23/2020 — 4/7/2020
        6: [(2020, 6, 15), (2020, 6, 29)],  # Round 6: 6/15/2020 — 6/29/2020
        7: [(2020, 9, 14), (2020, 9, 28)],  # Round 7: 9/14/2020 — 9/28/2020
    }

    for round, dates in date_ranges.items():
        round_start = utc.localize(datetime.datetime(*dates[0]))
        round_end = utc.localize(datetime.datetime(*dates[1]))

        if round_start < timestamp < round_end:
            return round

    return None

def get_converted_amount(amount, token_symbol):
    try:
        if token_symbol == "ETH" or token_symbol == "WETH":
            return Decimal(float(amount) * float(eth_usd_conv_rate()))
        else:
            value_token_to_eth = Decimal(convert_amount(
                amount,
                token_symbol,
                "ETH")
            )

        value_eth_to_usdt = Decimal(eth_usd_conv_rate())
        value_usdt = value_token_to_eth * value_eth_to_usdt
        return value_usdt

    except ConversionRateNotFoundError as e:
        try:
            return Decimal(convert_amount(
                amount,
                token_symbol,
                "USDT"))
        except ConversionRateNotFoundError as no_conversion_e:
            logger.info(no_conversion_e)
            return None


def get_user_code(user_id, grant, coding_set=block_codes, length=6):
    seed(user_id ** grant.id)
    coding_id = [coding_set[randint(0, 9)] for _ in range(length)]

    return ''.join(coding_id)


def add_grant_to_active_clrs(grant):
    from grants.models import Grant, GrantCLR

    active_clr_rounds = GrantCLR.objects.filter(is_active=True)
    for clr_round in active_clr_rounds:
        grants_in_clr = Grant.objects.filter(**clr_round.grant_filters)
        if grants_in_clr.filter(pk=grant.pk).count():
            grant.in_active_clrs.add(clr_round)
            grant.save()
