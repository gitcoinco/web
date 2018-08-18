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

from dashboard.models import Bounty, Interest
from marketing.mails import bounty_uninterested, new_match


class Command(BaseCommand):

    help = 'sends a test email'

    def handle(self, *args, **options):
        b = Bounty.objects.all().last()
        i = Interest.objects.all().last()
        # new_bounty(b, [settings.CONTACT_EMAIL])
        new_match([settings.CONTACT_EMAIL, 'ksowocki@gmail.com'], b, 'owocki')
        # weekly_roundup([settings.CONTACT_EMAIL])
        # new_bounty(b, [settings.CONTACT_EMAIL])
        # new_work_submission(b, [settings.CONTACT_EMAIL])
        # new_bounty_rejection(b, [settings.CONTACT_EMAIL])
        # new_bounty_acceptance(b, [settings.CONTACT_EMAIL])
        # bounty_expire_warning(b, [settings.CONTACT_EMAIL])
        bounty_uninterested([settings.CONTACT_EMAIL, 'ksowocki@gmail.com'], b, i)
