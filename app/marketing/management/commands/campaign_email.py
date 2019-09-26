# -*- coding: utf-8 -*-
'''
    Copyright (C) 2018 Gitcoin Core

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
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from marketing.mails import nth_day_email_campaign
from marketing.models import EmailSubscriber


def n_days_ago(n):
    before = timezone.now() - timezone.timedelta(days=n)
    return datetime(
        before.year, before.month, before.day,
        0, 0, 0, 0,
        tzinfo=timezone.get_current_timezone())


def send_nth_email_to_subscriber(nth, sub):
    first_email = EmailSubscriber.objects.filter(email__iexact=sub.email).order_by('created_on').first()
    if first_email.id == sub.id:
        # it is the first time this subscriber is in our system
        # send email to him/her
        nth_day_email_campaign(nth, sub)


def send_nth_email(nth):
    print('sending day {} email'.format(nth))
    # query all new subscribers created
    # may contain duplicated email addresses with different source
    subs = EmailSubscriber.objects.filter(
        created_on__gt=n_days_ago(nth),
        created_on__lte=n_days_ago(nth-1))
    for sub in subs:
        send_nth_email_to_subscriber(nth, sub)


class Command(BaseCommand):

    help = 'Send marketing email to new subscribers'

    def handle(self, *args, **options):
        # day 1 email has been sent
        # start from day 2
        for i in range(2, 3):
            send_nth_email(i)
