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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailchimp3 import MailChimp
from marketing.models import EmailSubscriber
from marketing.utils import get_or_save_email_subscriber as process_email

hours_ago = 12 #if you change, this make sure you change the crontab file to ...
# make it inclusive of all users since last run of this job


def pull_to_db():
    # setup
    before_timestamp = timezone.now() - timezone.timedelta(hours=hours_ago)

    print('- pull_to_db')
    print("- profile")
    from dashboard.models import Profile
    # right now, we only take profiles that've given us an access token
    profiles = Profile.objects.exclude(email='').filter(modified_on__gt=before_timestamp).all()
    # in the future, though, we could take ALL github profiles in the system and use those
    # profiles = Profile.objects.exclude(email='').all()
    for email in profiles.values_list('email', flat=True):
        process_email(email, 'profile_email')

    print("- match")
    from marketing.models import Match
    for email in Match.objects.filter(modified_on__gt=before_timestamp).values_list('email', flat=True):
        process_email(email, 'match')

    get_size = 50
    client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY, mc_user=settings.MAILCHIMP_USER)

    print('mailchimp')
    for i in range(0, 90000):
        members = client.lists.members.all(settings.MAILCHIMP_LIST_ID, count=get_size, offset=(i*get_size), fields="members.email_address")
        members = members['members']
        if not members:
            break
        print(i)
        for member in members:
            email = member['email_address']
            process_email(email, 'mailchimp')
    print('/mailchimp')

    print('local')
    print("- dashboard_sub")
    from dashboard.models import Subscription
    for email in Subscription.objects.filter(modified_on__gt=before_timestamp).values_list('email', flat=True):
        process_email(email, 'dashboard_subscription')

    print("- tip, Kudos")
    from dashboard.models import Tip
    from kudos.models import KudosTransfer
    objects = [Tip, KudosTransfer]
    for obj in objects:
        for _this in obj.objects.filter(modified_on__gt=before_timestamp):
            # do not add receive tip emails to the mailing list,
            # don't want to spam people at 4 diff email addresses
            # for email in tip.emails:
            #    process_email(email, 'tip_usage')
            if _this.from_email:
                process_email(_this.from_email, 'kudos_tip_usage')
            if _this.primary_email:
                process_email(_this.primary_email, 'kudos_tip_receive')

    print("- bounty")
    from dashboard.models import Bounty
    for b in Bounty.objects.filter(modified_on__gt=before_timestamp).prefetch_related('fulfillments').all():
        email_list = []
        if b.bounty_owner_email:
            email_list.append(b.bounty_owner_email)
        for fulfiller in b.fulfillments.all():
            if fulfiller.fulfiller_email:
                email_list.append(fulfiller.fulfiller_email)
        for email in email_list:
            process_email(email, 'bounty_usage')

    print("- tdi")
    from tdi.models import WhitepaperAccess, WhitepaperAccessRequest
    for email in WhitepaperAccess.objects.filter(modified_on__gt=before_timestamp).values_list('email', flat=True):
        process_email(email, 'whitepaperaccess')

    for email in WhitepaperAccessRequest.objects.filter(modified_on__gt=before_timestamp).values_list('email', flat=True):
        process_email(email, 'whitepaperaccessrequest')

    print('/pull_to_db')

def sync_mailchimp_list(eses, list_id):
    print("- {} emails".format(eses.count()))
    client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY, mc_user=settings.MAILCHIMP_USER)
    for es in eses.values_list('email', flat=True):
        email = es.email
        print(email)
        try:
            client.lists.members.create(list_id, {
                'email_address': email,
                'status': 'subscribed'
            })
            print('pushed_to_list')
        except Exception:
            # print("already on the list")
            pass


def push_to_mailchimp():
    print('- push_to_mailchimp')
    client = MailChimp(settings.MAILCHIMP_API_KEY, settings.MAILCHIMP_USER)
    created_after = timezone.now() - timezone.timedelta(hours=12)

    eses_funder = EmailSubscriber.objects.filter(
        active=True, created_on__gt=created_after,
        profile__persona_is_funder=True).order_by('-pk')
    print("funder emails")
    print("- {} emails".format(eses_funder.count()))
    sync_mailchimp_list(eses_funder, settings.MAILCHIMP_LIST_ID_FUNDERS)

    eses_hunter = EmailSubscriber.objects.filter(
        active=True, created_on__gt=created_after,
        profile__persona_is_hunter=True).order_by('-pk')
    print("hunter emails")
    print("- {} emails".format(eses_hunter.count()))
    sync_mailchimp_list(eses_hunter, settings.MAILCHIMP_LIST_ID_HUNTERS)

    eses = EmailSubscriber.objects.filter(active=True,
        created_on__gt=created_after).order_by('-pk')
    print("all emails")
    print("- {} emails".format(eses.count()))
    sync_mailchimp_list(eses, settings.MAILCHIMP_LIST_ID)

    print('/push_to_mailchimp')


class Command(BaseCommand):

    help = 'pulls mailchimp emails'

    def handle(self, *args, **options):
        pull_to_db()
        push_to_mailchimp()
