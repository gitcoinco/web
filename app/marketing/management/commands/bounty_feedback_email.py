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
from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment
from marketing.mails import bounty_feedback


class Command(BaseCommand):

    help = 'sends feedback emails to bounties that were closed in last xx hours, but only if its the first time a bounty has been accepted by taht persona'

    def handle(self, *args, **options):
        start_time = timezone.now() - timezone.timedelta(hours=48)
        end_time = timezone.now() - timezone.timedelta(hours=24)
        statues = ['done']
        bounties_last_timeperiod = Bounty.objects.filter(created_on__gt=start_time, created_on__lt=end_time, idx_status__in=statues)
        print(bounties_last_timeperiod.count())
        for bounty in bounties_last_timeperiod:

            submitter_email = bounty.bounty_owner_email
            previous_bounties = Bounty.objects.filter(created_on__lt=start_time, idx_status__in=statues, bounty_owner_email=submitter_email, current_bounty=True).exclude(pk=bounty.pk).distinct()
            has_been_sent_before_to_persona = previous_bounties.count()
            if not has_been_sent_before_to_persona:
                bounty_feedback(bounty, 'submitter', previous_bounties)

            accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
            if accepted_fulfillments.exists():
                accepted_fulfillment = accepted_fulfillments.first()
                fulfiller_email = accepted_fulfillment.fulfiller_email
                fulfillment_pks = BountyFulfillment.objects.filter(accepted=True, fulfiller_email=fulfiller_email).values__list('pk', flat=True)
                previous_bounties = Bounty.objects.filter(created_on__gt=start_time, idx_status__in=statues, fulfillments__pk__in=fulfillment_pks, current_bounty=True).exclude(pk=bounty.pk).distinct()
                has_been_sent_before_to_persona = previous_bounties.count()
                if not has_been_sent_before_to_persona:
                    bounty_feedback(bounty, 'funder', previous_bounties)
