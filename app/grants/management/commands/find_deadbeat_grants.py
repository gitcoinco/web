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

from marketing.mails import notify_deadbeat_grants


class Command(BaseCommand):

    help = 'finds quests whose reward is out of redemptions'

    def handle(self, *args, **options):
        from grants.models import Grant
        from django.utils import timezone
        before = timezone.now() - timezone.timedelta(hours=6)
        grants = Grant.objects.filter(contract_address='0x0', contract_version__lt=2, active=True, created_on__lt=before)
        if grants.count():
            notify_deadbeat_grants(grants)
