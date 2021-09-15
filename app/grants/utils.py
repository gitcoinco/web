# -*- coding: utf-8 -*-
"""Define the Grant utilities.

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

"""
import logging
import os
import re
import urllib.request
from datetime import datetime
from decimal import Decimal
from random import randint, seed
from secrets import token_hex

from django.utils import timezone

from app.settings import BASE_URL, MEDIA_URL, NOTION_API_KEY, NOTION_SYBIL_DB
from app.utils import notion_write
from avatar.utils import convert_img
from dashboard.models import Profile
from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate
from grants.sync.algorand import sync_algorand_payout
from grants.sync.binance import sync_binance_payout
from grants.sync.celo import sync_celo_payout
from grants.sync.harmony import sync_harmony_payout
from grants.sync.polkadot import sync_polkadot_payout
from grants.sync.rsk import sync_rsk_payout
from grants.sync.zcash import sync_zcash_payout
from grants.sync.zil import sync_zil_payout
from perftools.models import JSONStore, StaticJsonEnv
from PIL import Image, ImageDraw, ImageOps
from townsquare.models import SquelchProfile

logger = logging.getLogger(__name__)

block_codes = ('▖', '▗', '▘', '▙', '▚', '▛', '▜', '▝', '▞', '▟')
emoji_codes = ('🎉', '🎈', '🎁', '🎊', '🙌', '🥂', '🎆', '🔥', '⚡', '👍')


tenant_payout_mapper = {
    'ZCASH': sync_zcash_payout,
    'CELO': sync_celo_payout,
    'ZIL': sync_zil_payout,
    'HARMONY': sync_harmony_payout,
    'POLKADOT': sync_polkadot_payout,
    'BINANCE': sync_binance_payout,
    'KUSAMA': sync_polkadot_payout,
    'RSK': sync_rsk_payout,
    'ALGORAND': sync_algorand_payout
}

def get_clr_rounds_metadata():
    '''
        Fetches default CLR round metadata for stats/marketing flows.
        This is configured when multiple rounds are running
    '''
    try:
        CLR_ROUND_DATA = StaticJsonEnv.objects.get(key='CLR_ROUND').data

        clr_round = CLR_ROUND_DATA['round_num']
        start_date = CLR_ROUND_DATA['round_start']
        end_date = CLR_ROUND_DATA['round_end']
        round_active = CLR_ROUND_DATA['round_active']

        # timezones are in UTC (format example: 2021-06-16:15.00.00)
        round_start_date = datetime.strptime(start_date, '%Y-%m-%d:%H.%M.%S')
        round_end_date = datetime.strptime(end_date, '%Y-%m-%d:%H.%M.%S')

    except:
        # setting defaults
        clr_round=1
        round_start_date = timezone.now()
        round_end_date = timezone.now() + timezone.timedelta(days=14)
        round_active = True

    return clr_round, round_start_date, round_end_date, round_active

def get_upload_filename(instance, filename):
    salt = token_hex(16)
    file_path = os.path.basename(filename)
    return f"grants/{getattr(instance, '_path', '')}/{salt}/{file_path}"

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


def generate_collection_thumbnail(collection, width, heigth):
    grants = collection.grants.all()
    profile = collection.profile
    return generate_img_thumbnail_helper(grants, profile, width, heigth)


def generate_img_thumbnail_helper(grants, profile, width, heigth):
    MARGIN = int(width / 30)
    MID_MARGIN = int(width / 90)
    BG = (111, 63, 245)
    DISPLAY_GRANTS_LIMIT = 4
    PROFILE_WIDTH = PROFILE_HEIGHT = int(width / 3.5)
    GRANT_WIDTH = int(width / 2) - MARGIN - MID_MARGIN
    GRANT_HEIGHT = int(heigth / 2) - MARGIN - MID_MARGIN
    IMAGE_BOX = (width, heigth)
    LOGO_SIZE_DIFF = int(GRANT_WIDTH / 5)
    HALF_LOGO_SIZE_DIFF = int(LOGO_SIZE_DIFF / 2)
    PROFILE_BOX = (PROFILE_WIDTH - LOGO_SIZE_DIFF, PROFILE_HEIGHT - LOGO_SIZE_DIFF)
    GRANT_BOX = (GRANT_WIDTH, GRANT_HEIGHT)
    media_url = '' if 'media' not in MEDIA_URL else BASE_URL[:-1]

    logos = []
    for grant in grants:
        if grant.logo:
            if len(logos) > DISPLAY_GRANTS_LIMIT:
                break
            grant_url = f'{media_url}{grant.logo.url}'
            print(f'Trying to get: ${grant_url}')
            fd = urllib.request.urlopen(grant_url)
            logos.append(fd)
        else:
            static_file = f'assets/v2/images/grants/logos/{grant.id % 3}.png'
            logos.append(static_file)

    for logo in range(len(logos), 4):
        logos.append(None)

    thumbail = Image.new('RGBA', IMAGE_BOX, color=BG)
    avatar_url = f'{media_url}{profile.avatar_url}'
    fd = urllib.request.urlopen(avatar_url)

    # Make rounder profile avatar img
    mask = Image.new('L', PROFILE_BOX, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + PROFILE_BOX, fill=255)
    profile_thumbnail = Image.open(fd)

    profile_thumbnail.thumbnail(PROFILE_BOX, Image.ANTIALIAS)
    profile_circle = ImageOps.fit(profile_thumbnail, mask.size, centering=(0.5, 0.5))

    try:
        applied_mask = profile_circle.copy()
        applied_mask.putalpha(mask)
        profile_circle.paste(applied_mask, (0, 0), profile_circle)
    except ValueError:
        profile_circle.putalpha(mask)


    CORNERS = [
        [MARGIN, MARGIN],  # Top left grant
        [width - GRANT_WIDTH - MARGIN, MARGIN],  # Top right grant
        [MARGIN, heigth - GRANT_HEIGHT - MARGIN],  # bottom left grant
        [width - GRANT_WIDTH - MARGIN, heigth - GRANT_HEIGHT - MARGIN]  # bottom right grant
    ]

    for index in range(4):
        if logos[index] is None:
            grant_bg = Image.new('RGBA', GRANT_BOX, color='white')
            thumbail.paste(grant_bg, CORNERS[index], grant_bg)
            continue

        if type(logos[index]) is not str and re.match(r'.*\.svg', logos[index].url):
            grant_img = convert_img(logos[index])
            grant_thumbail = Image.open(grant_img)
        else:
            try:
                grant_thumbail = Image.open(logos[index])
            except ValueError:
                grant_thumbail = Image.open(logos[index]).convert("RGBA")

        grant_thumbail.thumbnail(GRANT_BOX, Image.ANTIALIAS)

        grant_bg = Image.new('RGBA', GRANT_BOX, color='white')

        try:
            grant_bg.paste(grant_thumbail, (int(GRANT_WIDTH / 2 - grant_thumbail.size[0] / 2),
                                            int(GRANT_HEIGHT / 2 - grant_thumbail.size[1] / 2)), grant_thumbail)
        except ValueError:
            grant_bg.paste(grant_thumbail, (int(GRANT_WIDTH / 2 - grant_thumbail.size[0] / 2),
                                            int(GRANT_HEIGHT / 2 - grant_thumbail.size[1] / 2)))

        thumbail.paste(grant_bg, CORNERS[index], grant_bg)

    draw_on_thumbnail = ImageDraw.Draw(thumbail)
    draw_on_thumbnail.ellipse([
        (int(width / 2 - PROFILE_WIDTH / 2), int(heigth / 2 - PROFILE_HEIGHT / 2)),
        (int(width / 2 + PROFILE_WIDTH / 2), int(heigth / 2 + PROFILE_HEIGHT / 2))
    ], fill="#6F3FF5")

    try:
        thumbail.paste(profile_circle, (int(width / 2 - PROFILE_WIDTH / 2) + HALF_LOGO_SIZE_DIFF, int(heigth / 2 - PROFILE_HEIGHT / 2) + HALF_LOGO_SIZE_DIFF),
                       profile_circle)
    except ValueError:
        thumbail.paste(profile_circle, (int(width / 2 - PROFILE_WIDTH / 2) + HALF_LOGO_SIZE_DIFF, int(heigth / 2 - PROFILE_HEIGHT / 2) + HALF_LOGO_SIZE_DIFF))

    return thumbail


def sync_payout(contribution):
    if not contribution:
        return None

    subscription = contribution.subscription

    if not subscription:
        return None

    tenant_payout_mapper[subscription.tenant](contribution)


def save_grant_to_notion(grant):
    """Post an insert to notions sybil-db table"""
    # check for notion credentials before attempting insert
    if NOTION_SYBIL_DB and NOTION_API_KEY:
        # fully qualified url
        fullUrl = BASE_URL.rstrip('/') + grant.url

        # write to NOTION_SYBIL_DB following the defined schema (returns dict of new object)
        return notion_write(NOTION_SYBIL_DB, {
            "Platform Status":{
                "id": "qwNU",
                "type": "select",
                "select":
                {
                    "id": "f38a5236-d1d7-4e63-ada0-e52a4e56d06f",
                    "name": "NEEDS REVIEW",
                    "color": "default"
                }
            },
            "Grant Name": {
                "id": "title",
                "type": "title",
                "title": [{
                    "type": "text",
                    "text": {
                        "content": fullUrl,
                        "link": {
                            "url": fullUrl
                        }
                    },
                    "plain_text": fullUrl,
                    "href": fullUrl
                }]
            }
        })


def toggle_user_sybil(sybil_users, non_sybil_users):
    '''util function which marks users as sybil/not'''

    squelched_profiles = SquelchProfile.objects.all()
    if sybil_users:
        # iterate through users which need to be packed as sybil
        for user in sybil_users:
            try:
                # get user profile
                profile = Profile.objects.get(pk=user.get('id'))
                label = user.get('label')
                comment = user.get('comment')

                # check if user has entry in SquelchProfile
                if (
                    not squelched_profiles.filter(profile=profile).first() and
                    label and comment
                ):
                    # mark user as sybil
                    SquelchProfile.objects.create(
                        profile=profile,
                        label=label,
                        comments=comment
                    )
            except Exception as e:
                print(f"error: unable to mark user ${user.get('id')} as sybil. {e}")

    if non_sybil_users:
        # iterate and remove sybil from user
        for user in non_sybil_users:
            try:
                profile = Profile.objects.get(pk=user.get('id'))
                squelched_profiles.filter(profile=profile).delete()
            except Exception as e:
                print(f"error: unable to mark ${user.get('id')} as non sybil. {e}")



def bsci_script(csv):
    # TODO-BSCI: install import
    import pandas as pd
    import numpy as np

    try:

        # choose the specific csv you want to use
        endpoint_df = pd.read_csv(csv)

        sybil_df = pd.DataFrame()
        non_sybil_df = pd.DataFrame()
        '''
        filters human labeled sybils ('reviewer_is_certain (0/1)' and 'is_sybil_y' values can be adjusted)
        human_sybil_score could also be used as a filter is wanted
        '''
        human_sybil = endpoint_df[(endpoint_df['flag_type_y'] == 'Human') & (endpoint_df['reviewer_is_certain (0/1)_y'] >= 0.99)  & (endpoint_df['is_sybil_y'] >= 0.99)]
        endpoint_df = endpoint_df[~endpoint_df.handle.isin(human_sybil.handle)]
        human_sybil = human_sybil[['handle', 'flag_type_y', 'notes']]
        human_sybil = human_sybil.rename({'handle': 'id', 'flag_type_y': 'label', 'notes': 'comment'}, axis = 1, inplace = True)
        sybil_df = sybil_df.append(human_sybil)

        '''
        filters heuristic labeled sybils, nothing can be adjusted here
        '''
        heuristic_sybil = endpoint_df[(endpoint_df['flag_type_x'] == 'Heuristic') & (endpoint_df['ml_score'] >= 0.99)]
        endpoint_df = endpoint_df[~endpoint_df.handle.isin(heuristic_sybil.handle)]
        heuristic_sybil = heuristic_sybil[['handle', 'flag_type_x', 'notes']]
        hueristic_sybil = heuristic_sybil.rename({'handle': 'id', 'flag_type_x': 'label', 'notes': 'comment'}, axis = 1, inplace = True)
        sybil_df = sybil_df.append(heuristic_sybil)

        '''
        filters ml predicted sybils, ml_score can be adjusted to be either higher or lower
        higher ml_score means less people are likely to appeal, but potentially some sybils slip through
        lower ml_score means more people are likely to appeal, but more sybils are potentially caught
        '''
        ml_sybil = endpoint_df[(endpoint_df['flag_type_x'] == 'Prediction') & (endpoint_df['ml_score'] >= 0.9)]
        endpoint_df = endpoint_df[~endpoint_df.handle.isin(ml_sybil.handle)]
        ml_sybil = ml_sybil[['handle', 'flag_type_x', 'notes']]
        ml_sybil = ml_sybil.rename({'handle': 'id', 'flag_type_x': 'label', 'notes': 'comment'}, axis = 1, inplace = True)
        sybil_df = sybil_df.append(ml_sybil)

        '''
        filters human labeled non-sybil users
        nothing here should be changed as these are just the remaining users that were marked by humans not included in the sybil filtering
        '''
        human_non_sybil = endpoint_df[(endpoint_df['flag_type_y'] == 'Human') & (endpoint_df['reviewer_is_certain (0/1)_y'] != np.nan)]
        endpoint_df = endpoint_df[~endpoint_df.handle.isin(human_non_sybil.handle)]
        human_non_sybil = human_non_sybil[['handle', 'flag_type_y', 'notes']]
        human_non_sybil = human_non_sybil.rename({'handle': 'id', 'flag_type_y': 'label', 'notes': 'comment'}, axis = 1, inplace = True)
        non_sybil_df = non_sybil_df.append(human_non_sybil)

        '''
        filters heuristic non sybils, nothing here needs to be adjusted
        '''
        heuristic_non_sybil = endpoint_df[(endpoint_df['flag_type_x'] == 'Heuristic') & (endpoint_df['ml_score'] <= 0.01)]
        endpoint_df = endpoint_df[~endpoint_df.handle.isin(heuristic_non_sybil.handle)]
        heuristic_non_sybil = heuristic_non_sybil[['handle', 'flag_type_x', 'notes']]
        hueristic_non_sybil = heuristic_non_sybil.rename({'handle': 'id', 'flag_type_x': 'label', 'notes': 'comment'}, axis = 1, inplace = True)
        non_sybil_df = non_sybil_df.append(heuristic_non_sybil)

        '''
        This just filters out the remaining users that were not filtered in the previous sections, nothing can be adjusted here
        '''
        ml_non_sybil = endpoint_df
        ml_non_sybil = ml_non_sybil[['handle', 'flag_type_x', 'notes']]
        ml_non_sybil = ml_non_sybil.rename({'handle': 'id', 'flag_type_x': 'label', 'notes': 'comment'}, axis = 1, inplace = True)
        non_sybil_df = non_sybil_df.append(ml_non_sybil)

        '''
        conversion of all the data so that it can be pushed to the toggle_user_sybil endpoint
        '''
        #sybil_df = ml_df[ml_df['ml_score'] >= 0.9 and ml_df['flag_type'] != 'Human']
        sybil_users = sybil_df.to_dict('records')
        non_sybil_users = non_sybil_df.to_dict('records')

        print(sybil_users)
        print(non_sybil_users)
        # TODO-BSCI: validate
        toggle_user_sybil(sybil_users, non_sybil_users)

        # endpoint_dict = {"sybil_users": None, "non_sybil_users": None}
        # endpoint_dict['sybil_users'] = sybil_endpoint
        # endpoint_dict['non_sybil_users'] = non_sybil_endpoint
        # endpoint_json = json.dumps(endpoint_dict)
        #requests.post('https://gitcoin.co/grants/v1/api/toggle_user_sybil', data = endpoint_json)
    except Exception as e:
        logger.error(f'error: bsci_sybil_script - {e}')
