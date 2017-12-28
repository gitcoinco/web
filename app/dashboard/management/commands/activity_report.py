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

import argparse
import csv
import datetime
import re
import StringIO
from itertools import imap

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Tip
from marketing.mails import send_mail

DATE_FORMAT = '%Y/%m/%d'
def valid_date(v):
    try:
        return datetime.datetime.strptime(v, DATE_FORMAT)
    except ValueError:
        raise argparse.ArgumentTypeError('%s is not a date in YYYY/MM/DD format' % v)

GITHUB_REPO_PATTERN = re.compile('github.com/[\w-]+/([\w-]+)')

def extract_github_repo(url):
    match = GITHUB_REPO_PATTERN.search(url)
    if not match:
        raise Exception("malformed github url: %s", url)

    return match.groups()[0]

def format_bounty(bounty):
    return {
        'type': 'bounty',
        'created_on': bounty.created_on,
        'last_activity': bounty.modified_on,
        'amount': bounty.value_in_token,
        'denomnation': bounty.token_name,
        'amount_eth': bounty.value_in_eth,
        'amount_usdt': bounty.value_in_usdt,
        'from_address': bounty.bounty_owner_address,
        'to_address': bounty.claimee_address,
        'repo': extract_github_repo(bounty.github_url),
        'from_username': bounty.bounty_owner_github_username or '', # XXX owner can be null
        'to_username': bounty.claimee_github_username or '', # XXX claimee can be null
        'status': bounty.status,
        'comments': 'no bounty comments right now' # XXX where does the PR link come from?
    }

def format_tip(tip):
    return {
        'type': 'tip',
        'created_on': tip.created_on,
        'last_activity': tip.modified_on,
        'amount': tip.amount,
        'denomnation': tip.tokenName,
        'amount_eth': tip.value_in_eth,
        'amount_usdt': tip.value_in_usdt,
        'from_address': 'tip has no owner address saved', # XXX owner address field can't be populated with current schema
        'to_address': 'tip has no claimee', # XXX claimee address field doesn't make sense for tips
        'repo': extract_github_repo(tip.github_url) if tip.github_url else '', # XXX url can be null
        'from_username': tip.from_email, # XXX github owner field doesn't make sense for tips
        'to_username': 'tip has no claimee', # XXX github claimee field doesn't make sense for tips
        'status': tip.status,
        'comments': 'no no tip comments right now' # XXX comment field doesn't make sense for tips
    }

def itermerge(gen_a, gen_b, key):
    a = None
    b = None

    # yield items in order until first iterator is emptied
    try:
        while True:
            if a is None:
                a = gen_a.next()

            if b is None:
                b = gen_b.next()

            if key(a) <= key(b):
                yield a
                a = None
            else:
                yield b
                b = None
    except StopIteration:
        # yield last item to be pulled from non-empty iterator
        if a is not None:
            yield a

        if b is not None:
            yield b

    # flush remaining items in non-empty iterator
    try:
        for a in gen_a:
            yield a
    except StopIteration:
        pass

    try:
        for b in gen_b:
            yield b
    except StopIteration:
        pass


class Command(BaseCommand):

    help = 'emails activity report of tips and bounties to settings.CONTACT_EMAIL'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=valid_date, help='Start of date range (inclusive) in YYYY/MM/DD format for activities to be collected')
        parser.add_argument('end_date', type=valid_date, help='End of date range (inclusive) in YYYY/MM/DD format for activities to be collected')

    def handle(self, *args, **options):
        bounties = Bounty.objects.filter(
            network='mainnet',
            current_bounty=True,
            created_on__gte=options['start_date'],
            created_on__lte=options['end_date']
        ).order_by('created_on', 'id')

        tips = Tip.objects.filter(
            network='mainnet',
            created_on__gte=options['start_date'],
            created_on__lte=options['end_date']
        ).order_by('created_on', 'id')

        formatted_bounties = imap(format_bounty, bounties)
        formatted_tips = imap(format_tip, tips)

        csvfile = StringIO.StringIO()
        csvwriter = csv.DictWriter(csvfile, fieldnames=[
            'type', 'created_on', 'last_activity', 'amount', 'denomination', 'amount_eth',
            'amount_usdt', 'from_address', 'to_address', 'repo', 'from_username',
            'to_username', 'status', 'comments'])

        has_rows = False
        for item in itermerge(formatted_bounties, formatted_tips, lambda x: x['created_on']):
            has_rows = True
            csvwriter.writerow(item)

        start = options['start_date'].strftime(DATE_FORMAT)
        end = options['end_date'].strftime(DATE_FORMAT)
        if has_rows:
            subject = 'Gitcoin Activity report from %s to %s' % (start, end)
            send_mail(settings.CONTACT_EMAIL, settings.CONTACT_EMAIL, subject, csvfile.getvalue())

            self.stdout.write(self.style.SUCCESS('Sent activity report from %s to %s to %s' % (start, end, settings.CONTACT_EMAIL)))
        else:
            self.stdout.write(self.style.WARNING('No activity from %s to %s to report' % (start, end)))
