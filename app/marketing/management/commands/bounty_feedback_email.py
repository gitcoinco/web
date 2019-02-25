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

from dashboard.models import Bounty, BountyFulfillment
from marketing.mails import bounty_feedback


class Command(BaseCommand):

    help = 'sends feedback emails to bounties that were closed in last xx hours, but only if its the first time a bounty has been accepted by taht persona'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        start_time = timezone.now() - timezone.timedelta(hours=36)
        end_time = timezone.now() - timezone.timedelta(hours=12)
        statues = ['done', 'cancelled']
        bounties_fulfilled_last_timeperiod = Bounty.objects.current().filter(
            network='mainnet',
            fulfillment_accepted_on__gt=start_time,
            fulfillment_accepted_on__lt=end_time,
            idx_status='done'
            ).values_list('pk', flat=True)
        bounties_cancelled_last_timeperiod = Bounty.objects.current().filter(
            network='mainnet',
            canceled_on__gt=start_time,
            canceled_on__lt=end_time,
            idx_status='cancelled'
            ).values_list('pk', flat=True)
        bounty_pks = list(bounties_cancelled_last_timeperiod) + list(bounties_fulfilled_last_timeperiod)
        bounties_to_process = Bounty.objects.filter(pk__in=bounty_pks)
        print(bounties_to_process.count())
        for bounty in bounties_to_process:

            # identity
            submitter_email = bounty.bounty_owner_email
            is_fulfiller_and_funder_same_person = False

            # send email to the fulfiller
            accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
            if accepted_fulfillments.exists() and bounty.status == 'done':
                accepted_fulfillment = accepted_fulfillments.first()
                fulfiller_email = accepted_fulfillment.fulfiller_email
                is_fulfiller_and_funder_same_person = (fulfiller_email == submitter_email)
                fulfillment_pks = BountyFulfillment.objects.filter(accepted=True, fulfiller_email=fulfiller_email).values_list('pk', flat=True)
                previous_bounties = Bounty.objects.current().filter(idx_status__in=statues, fulfillments__pk__in=fulfillment_pks).exclude(pk=bounty.pk).distinct()
                has_been_sent_before_to_persona = previous_bounties.count()
                if not has_been_sent_before_to_persona and not is_fulfiller_and_funder_same_person:
                    bounty_feedback(bounty, 'fulfiller', previous_bounties)

            # send email to the funder
            previous_bounties = Bounty.objects.filter(idx_status__in=statues, bounty_owner_email=submitter_email, current_bounty=True).exclude(pk=bounty.pk).distinct()
            has_been_sent_before_to_persona = previous_bounties.count()
            if not has_been_sent_before_to_persona and not is_fulfiller_and_funder_same_person:
                bounty_feedback(bounty, 'funder', previous_bounties)
