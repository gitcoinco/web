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
from django.conf import settings
from django.core.management.base import BaseCommand

from mailchimp3 import MailChimp
from marketing.utils import get_or_save_email_subscriber as process_email


class Command(BaseCommand):

    help = 'pulls mailchimp emails'

    def handle(self, *args, **options):

        print("- match")
        from marketing.models import Match
        for match in Match.objects.all():
            process_email(match.email, 'match')


        get_size = 50
        client = MailChimp(settings.MAILCHIMP_USER, settings.MAILCHIMP_API_KEY)

        print('mailchimp')
        for i in range(0, 90000):
            members = client.lists.members.all(settings.MAILCHIMP_LIST_ID, count=get_size, offset=(i*get_size), fields="members.email_address")
            members = members['members']
            if not len(members):
                break
            print(i)
            for member in members:
                email = member['email_address']
                process_email(email, 'mailchimp')
        #TODO: could sync back
        #with client.lists.members.create(
        print('/mailchimp')

        print('local')
        print("- dashboard_sub")
        from dashboard.models import Subscription
        for sub in Subscription.objects.all():
            email = sub.email
            process_email(email, 'dashboard_subscription')

        print("- tip")
        from dashboard.models import Tip
        for tip in Tip.objects.all():
            for email in tip.emails:
                process_email(email, 'tip_usage')
            if tip.from_email:
                process_email(tip.from_email, 'tip_usage')

        print("- bounty")
        from dashboard.models import Bounty
        for b in Bounty.objects.all():
            email_list = []
            if b.bounty_owner_email:
                email_list.append(b.bounty_owner_email)
            if b.claimee_email:
                email_list.append(b.claimee_email)
            for email in email_list:
                process_email(email, 'bounty_usage')

        print("- tdi")
        from tdi.models import WhitepaperAccess, WhitepaperAccessRequest
        for wa in WhitepaperAccess.objects.all():
                process_email(wa.email, 'whitepaperaccess')

        for wa in WhitepaperAccessRequest.objects.all():
                process_email(wa.email, 'whitepaperaccessrequest')


        print('/local')
