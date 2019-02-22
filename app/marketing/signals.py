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

from django.db.models.signals import post_save
from django.dispatch import receiver

from marketing.mails import nth_day_email_campaign
from marketing.models import EmailSubscriber


@receiver(post_save, sender=EmailSubscriber)
def create_email_subscriber(sender, instance, created, **kwargs):
    if created:
        if not EmailSubscriber.objects.filter(email=instance.email).exclude(id=instance.id).exists():
            # this subscriber is the first time shown in our db
            # send email
            nth_day_email_campaign(1, instance)
