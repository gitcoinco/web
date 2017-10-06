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
from dashboard.models import Bounty
from django.utils import timezone
from marketing.mails import weekly_roundup


class Command(BaseCommand):

    help = 'the weekly roundup emails'

    def handle(self, *args, **options):
        days_back = 90

        email_list = []
        # todo: tip emails
        # mailchimp emails
        # whitepaper dev emails
        bounties = Bounty.objects.filter(web3_created__gt=timezone.now()-timezone.timedelta(days=days_back)).all()

        for b in bounties:
            if b.bounty_owner_email:
                email_list.append(b.bounty_owner_email)
            if b.claimee_email:
                email_list.append(b.claimee_email)
        email_list = set(email_list)

        print(email_list)
        print("got {} emails".format(len(email_list)))
        #TODO: formalize the list management into its own database table, completely with ability to manage subscriptions

        for to_email in email_list:
            weekly_roundup([to_email])
