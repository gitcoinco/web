'''
    Copyright (C) 2019 Gitcoin Core

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
import csv
import os
import warnings

from django.core.management.base import BaseCommand

from dashboard.models import Bounty, Profile, Tip

# Constants
DATETIME = 'datetime'
COUNTER_PARTY_NAME = 'counter_party_name'
COUNTER_PARTY_LOCATION = 'counter_party_location'
TOKEN_AMOUNT = 'token_amount'
TOKEN_NAME = 'token_name'
USD_VALUE = 'usd_value'
WORKER_TYPE = 'worker_type'
COUNTRY_CODE = 'country_code'

WEB3_NETWORK = 'rinkeby'
BOUNTY = 'bounty'
TIP = 'tip'
GRANT = 'grant'

FUNDERS_DIR = 'funders_csv'
TAX_YEAR = 2019

warnings.filterwarnings("ignore", category=DeprecationWarning)

us_workers = {}


def create_csv_record(profiles_obj, wt_obj, worker_type):
    record = {DATETIME: wt_obj.web3_created}

    if worker_type == BOUNTY:
        counter_party_name = []
        counter_party_location = []
        for fulfiller in wt_obj.fulfillments.filter(accepted=True):
            counter_party_name.append(fulfiller.fulfiller_github_username)
            if fulfiller.fulfiller_github_username not in us_workers.keys():
                us_workers[fulfiller.fulfiller_github_username] = 0
            us_workers[fulfiller.fulfiller_github_username] += wt_obj._val_usd_db
            profiles = profiles_obj.filter(handle__iexact=fulfiller.fulfiller_github_username)
            if profiles.exists():
                profile = profiles.first()
                if profile.location:
                    counter_party_location.append(profile.location)
                elif profile.locations:
                    counter_party_location.append(profile.locations[-1][COUNTRY_CODE])
                else:
                    counter_party_location.append('No location')
            # No profile found on DB
            else:
                counter_party_location.append('No profile')
        record[USD_VALUE] = wt_obj._val_usd_db

    elif worker_type == TIP:
        counter_party_name = wt_obj.username
        counter_party_location = 'No location'
        profiles = Profile.objects.filter(handle__iexact=wt_obj.username)
        if profiles.exists():
            profile = profiles.first()
            if profile.location:
                counter_party_location = profile.location
            elif profile.locations:
                counter_party_location = profiles.location[-1][COUNTRY_CODE]
        record[USD_VALUE] = wt_obj._value_in_usdt_now

    elif worker_type == GRANT:
        # TODO
        print('grant')

    record[COUNTER_PARTY_NAME] = counter_party_name
    record[COUNTER_PARTY_LOCATION] = counter_party_location
    record[TOKEN_AMOUNT] = wt_obj.value_in_token
    record[TOKEN_NAME] = wt_obj.token_name
    record[USD_VALUE] = wt_obj._val_usd_db
    record[WORKER_TYPE] = worker_type

    return record


def create_1099():
    print('1099')


class Command(BaseCommand):
    help = 'the tax report for last year'

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        funders = {}
        for p in profiles:
            # Bounty
            for b in p.get_sent_bounties:
                if not b._val_usd_db or b.status != 'done' or b.is_open is True or b.network != WEB3_NETWORK or p.username != b.bounty_owner_github_username:
                    continue
                else:
                    if b.fulfillment_accepted_on.date().year == TAX_YEAR:
                        if p.username not in funders.keys():
                            funders[p.username] = []
                        funders[p.username].append(create_csv_record(profiles, b, BOUNTY))
            # Tip
            for t in p.get_sent_tips:
                if not t.value_in_usdt_now or t.network != WEB3_NETWORK or p.username != t.from_username:
                    continue
                else:
                    if p.username not in funders.keys():
                        funders[p.username] = []
                    funders[p.username].append(create_csv_record(profiles, t, TIP))
            # Grant
            for g in p.get_my_grants:
                if g.network != WEB3_NETWORK:
                    continue
                else:
                    if p.username not in funders.keys():
                        funders[p.username] = []
                    funders[p.username].append(create_csv_record(profiles, g, GRANT))

        # check for create 1099
        for us_w, usd_value in us_workers.items():
            print(us_w)
            print(usd_value)
            profile = profiles.filter(handle__iexact=us_w)
            print(profile)
            # if value > 600$ then create 1099s for user

        csv_columns = [DATETIME, COUNTER_PARTY_NAME, COUNTER_PARTY_LOCATION, TOKEN_AMOUNT, TOKEN_NAME, USD_VALUE, WORKER_TYPE]
        if not os.path.isdir(os.path.join(os.getcwd(), FUNDERS_DIR)):
            os.makedirs(os.path.join(os.getcwd(), FUNDERS_DIR))
        for funder in funders:
            try:
                with open(os.path.join(os.getcwd(), FUNDERS_DIR, funder + '.csv'), 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    writer.writeheader()
                    for row in funders[funder]:
                        writer.writerow(row)
            except IOError:
                print("I/O error")
