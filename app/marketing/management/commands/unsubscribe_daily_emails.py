# -*- coding: utf-8 -*-
"""Define the GDPR reconsent command for EU users.

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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from marketing.mails import gdpr_reconsent
from marketing.models import EmailEvent, EmailSubscriber
from marketing.common.utils import allowed_to_send_email

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Command(BaseCommand):

    help = 'unsubscribes people from their daily emails if they are not reading them, per https://gitcoincore.slack.com/archives/CB1N0L6F7/p1594141095159400'

    def handle(self, *args, **options):
        days = 90 if settings.DEBUG else 30
        time_threshold = timezone.now() - timezone.timedelta(days=days)
        eses = EmailSubscriber.objects.order_by('-created_on')
        email_type_sendgrid = "new_bounty_daily"
        email_type_settings = 'new_bounty_notifications'
        for es in eses:
            if allowed_to_send_email(es.email, email_type_settings):
                base_email_events = EmailEvent.objects.filter(email=es.email, created_on__gt=time_threshold, category__icontains=email_type_sendgrid)
                num_sends = base_email_events.filter(event='delivered').count()
                num_opens = base_email_events.filter(event='open').count()
                num_clicks = base_email_events.filter(event='click').count()

                do_unsubscribe = num_sends > 5 and num_opens < 1 and num_clicks < 1
                if do_unsubscribe:
                    unsubscribed_email_type = {}
                    unsubscribed_email_type[email_type_settings] = True
                    es.build_email_preferences(unsubscribed_email_type)
                    print(f"unsubscribed {es.email} {num_clicks} {num_opens} {num_clicks}")
                    es.save()
