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
import time
import warnings
from datetime import datetime

from django.core.management.base import BaseCommand

from marketing.mails import gdpr_reconsent
from marketing.models import EmailSubscriber

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Command(BaseCommand):

    help = 'sends a GDPR re-consent form to all EU residents'

    def handle(self, *args, **options):
        if datetime.now() > datetime(2018, 5, 26):
            print("cannot send after GDPR is already live.. this email has already been sent")
            exit()

        queryset = EmailSubscriber.objects.all()
        print(f"got {queryset.count()} emails")

        counter = 0
        for es in queryset:
            if es.is_eu:
                counter += 1
                print(f"-sending {counter} / {es.email}")
                try:
                    gdpr_reconsent(es.email)
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    time.sleep(5)
