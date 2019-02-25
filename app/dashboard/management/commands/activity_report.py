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

import argparse
import csv
import datetime
import os
import re
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand

import boto
from boto.s3.key import Key
from dashboard.models import Bounty, Profile
from dashboard.utils import all_sendcryptoasset_models
from economy.utils import convert_amount
from enssubdomain.models import ENSSubdomainRegistration
from faucet.models import FaucetRequest
from marketing.mails import send_mail

DATE_FORMAT = '%Y/%m/%d'
DATE_FORMAT_HYPHENATED = '%Y-%m-%d'
REPORT_URL_EXPIRATION_TIME = 60 * 60 * 24 * 30  # seconds

GITHUB_REPO_PATTERN = re.compile(r'github.com/[\w-]+/([\w-]+)')

imap = map


def get_bio(handle):
    try:
        profile = Profile.objects.filter(handle=handle.replace('@', '')).first()
        return profile.data.get('location', 'unknown'), profile.data.get('bio', 'unknown')
    except Exception:
        return 'unknown', 'unknown'


def valid_date(v):
    try:
        return datetime.datetime.strptime(v, DATE_FORMAT)
    except ValueError:
        raise argparse.ArgumentTypeError('%s is not a date in YYYY/MM/DD format' % v)


class Command(BaseCommand):

    help = 'emails activity report of tips and bounties to settings.CONTACT_EMAIL'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=valid_date, help='Start of date range (inclusive) in YYYY/MM/DD format for activities to be collected')
        parser.add_argument('end_date', type=valid_date, help='End of date range (inclusive) in YYYY/MM/DD format for activities to be collected')

    def extract_github_repo(self, url):
        match = GITHUB_REPO_PATTERN.search(url)
        if not match:
            self.stdout.write(self.style.WARNING('WARNING: malformed github url: %s, using value as is' % url))
            return url

        return match.groups()[0]

    def format_bounty(self, bounty):
        from dashboard.models import BountyFulfillment
        try:
            bounty_fulfillment = bounty.fulfillments.filter(accepted=True).latest('created_on')
            claimee_address = bounty_fulfillment.fulfiller_address
            fulfiller_github_username = bounty_fulfillment.fulfiller_github_username
        except BountyFulfillment.DoesNotExist:
            claimee_address = ''
            fulfiller_github_username = ''

        location, bio = get_bio(fulfiller_github_username)

        return {
            'type': 'bounty',
            'created_on': bounty.web3_created,
            'last_activity': bounty.modified_on,
            'amount': bounty.get_natural_value(),
            'denomination': bounty.token_name,
            'amount_eth': bounty.value_in_eth / 10**18 if bounty.value_in_eth else None,
            'amount_usdt': bounty.value_in_usdt,
            'from_address': bounty.bounty_owner_address,
            'claimee_address': claimee_address,
            'repo': self.extract_github_repo(bounty.github_url),
            'from_username': bounty.bounty_owner_github_username or '',
            'fulfiller_github_username': fulfiller_github_username,
            'status': bounty.status,
            'comments': bounty.github_url,
            'payee_bio': bio,
            'payee_location': location,
        }
        
    def format_cryptoasset(self, ca):
        _type = type(ca)
        location, bio = get_bio(ca.username)

        return {
            'type': _type,
            'created_on': ca.created_on,
            'last_activity': ca.modified_on,
            'amount': ca.amount_in_whole_units,
            'denomination': ca.tokenName,
            'amount_eth': ca.value_in_eth,
            'amount_usdt': ca.value_in_usdt,
            'from_address': ca.from_address,
            'claimee_address': ca.receive_address,
            'repo': self.extract_github_repo(ca.github_url) if ca.github_url else '',
            'from_username': ca.from_name,
            'fulfiller_github_username': ca.username,
            'status': ca.status,
            'comments': ca.github_url,
            'payee_bio': bio,
            'payee_location': location,
        }

    def format_faucet_distribution(self, fr):
        location, bio = get_bio(fr.github_username)

        return {
            'type': 'faucet_distribution',
            'created_on': fr.created_on,
            'last_activity': fr.modified_on,
            'amount': fr.amount,
            'denomination': 'ETH',
            'amount_eth': fr.amount,
            'amount_usdt': convert_amount(fr.amount, 'ETH', 'USDT'),
            'from_address': '0x4331B095bC38Dc3bCE0A269682b5eBAefa252929',
            'claimee_address': fr.address,
            'repo': 'n/a',
            'from_username': 'admin',
            'fulfiller_github_username': fr.github_username,
            'status': 'sent',
            'comments': f"faucet distribution {fr.pk}",
            'payee_bio': bio,
            'payee_location': location,
        }

    def format_ens_reg(self, ensreg):
        location, bio = get_bio(ensreg.profile.handle) if ensreg.profile else "", ""
        amount = ensreg.gas_cost_eth
        return {
            'type': 'ens_subdomain_registration',
            'created_on': ensreg.created_on,
            'last_activity': ensreg.modified_on,
            'amount': amount,
            'denomination': 'ETH',
            'amount_eth': amount,
            'amount_usdt': convert_amount(amount, 'ETH', 'USDT'),
            'from_address': '0x4331B095bC38Dc3bCE0A269682b5eBAefa252929',
            'claimee_address': ensreg.subdomain_wallet_address,
            'repo': 'n/a',
            'from_username': 'admin',
            'fulfiller_github_username': ensreg.profile.handle if ensreg.profile else "",
            'status': 'sent',
            'comments': f"ENS Subdomain Registration {ensreg.pk}",
            'payee_bio': bio,
            'payee_location': location,
        }

    def upload_to_s3(self, filename, contents):
        s3 = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = s3.get_bucket(settings.S3_REPORT_BUCKET)
        key = Key(bucket)
        key.key = os.path.join(settings.S3_REPORT_PREFIX, filename)
        key.set_contents_from_string(contents)
        return key.generate_url(expires_in=REPORT_URL_EXPIRATION_TIME)

    def handle(self, *args, **options):
        bounties = Bounty.objects.prefetch_related('fulfillments').current().filter(
            network='mainnet',
            web3_created__gte=options['start_date'],
            web3_created__lte=options['end_date']
        ).order_by('web3_created', 'id')
        formatted_bounties = imap(self.format_bounty, bounties)

        frs = FaucetRequest.objects.filter(
            created_on__gte=options['start_date'],
            created_on__lte=options['end_date'],
            fulfilled=True,
        ).order_by('created_on', 'id')
        formatted_frs = imap(self.format_faucet_distribution, frs)

        all_scram = []
        for _class in all_sendcryptoasset_models():
            objs = _class.objects.filter(
                network='mainnet',
                created_on__gte=options['start_date'],
                created_on__lte=options['end_date']
            ).send_success().order_by('created_on', 'id')
            objs = imap(self.format_cryptoasset, objs)
            objs = [x for x in objs]
            all_scram += objs

        enssubregistrations = ENSSubdomainRegistration.objects.filter(
            created_on__gte=options['start_date'],
            created_on__lte=options['end_date']
        ).order_by('created_on', 'id')
        formted_enssubreg = imap(self.format_ens_reg, enssubregistrations)

        # python3 list hack
        formatted_frs = [x for x in formatted_frs]
        formatted_bounties = [x for x in formatted_bounties]
        formateted_enssubregistrations = [x for x in formted_enssubreg]
        all_items = formatted_bounties + all_scram + formatted_frs + formateted_enssubregistrations

        csvfile = StringIO()
        csvwriter = csv.DictWriter(csvfile, fieldnames=[
            'type', 'created_on', 'last_activity', 'amount', 'denomination', 'amount_eth',
            'amount_usdt', 'from_address', 'claimee_address', 'repo', 'from_username',
            'fulfiller_github_username', 'status', 'comments', 'payee_bio', 'payee_location'])
        csvwriter.writeheader()

        items = sorted(all_items, key=lambda x: x['created_on'])
        has_rows = False
        for item in items:
            has_rows = True
            csvwriter.writerow(item)

        start = options['start_date'].strftime(DATE_FORMAT_HYPHENATED)
        end = options['end_date'].strftime(DATE_FORMAT_HYPHENATED)
        now = str(datetime.datetime.now())
        if has_rows:
            subject = f'Gitcoin Activity report from {start} to {end}'

            url = self.upload_to_s3(f'activity_report_{start}_{end}_generated_on_{now}.csv', csvfile.getvalue())
            body = f'<a href="{url}">{url}</a>'
            print(url)

            send_mail(
                settings.CONTACT_EMAIL,
                settings.CONTACT_EMAIL,
                subject,
                body='',
                html=body,
                categories=['admin', 'activity_report'],
            )

            self.stdout.write(
                self.style.SUCCESS('Sent activity report from %s to %s to %s' % (start, end, settings.CONTACT_EMAIL))
            )
        else:
            self.stdout.write(self.style.WARNING('No activity from %s to %s to report' % (start, end)))
