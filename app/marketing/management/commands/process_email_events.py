'''
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

'''

from django.core.management.base import BaseCommand
from django.utils import timezone

from marketing.models import EmailEvent, EmailSubscriber
from retail.emails import ALL_EMAILS


def num_total_bounces(email):
        return EmailEvent.objects.filter(
            event__in=['bounce'],
            email__iexact=email,
            ).count()


class Command(BaseCommand):

    help = 'pulls any email events we need to manage and puts those emails on the suppression list'

    def handle(self, *args, **options):
        hours = 24
        bounce_threshold = 5
        
        email_events = EmailEvent.objects.filter(
            event__in=['spamreport', 'bounce'],
            created_on__gt=timezone.now()-timezone.timedelta(hours=hours)
            )

        for ee in email_events:
            print(ee)
            try:
                bounces = num_total_bounces(ee.email)

                should_unsubscribe = bounces > bounce_threshold or ee.event == 'spamreport' 
                if should_unsubscribe:
                    es = EmailSubscriber.objects.filter(email=ee.email).first()
                    # auto unsubscribe
                    suppression_preferences = {ele[0]:True for ele in ALL_EMAILS}
                    es.preferences['suppression_preferences'] = suppression_preferences
                    es.form_submission_records += [f"auto unsubscribed all on {timezone.now()} because of email event {ee.pk} "]
                    es.save()
                    print(ee.pk, es.pk)
            except Exception as e:
                print(e)
