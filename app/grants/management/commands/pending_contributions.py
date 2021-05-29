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

from grants.models import Contribution
from marketing.mails import pending_contribution


class Command(BaseCommand):
    help = 'Send reminder for pending grant contributions- This is a scenario where funds were deposited into their Gitcoin zkSync account, but the user didnt keep the page open to finish chekout. So funds are "stuck" there until the revisit the cart and complete checkout'

    def handle(self, *args, **options):
        contributions = Contribution.objects.filter(
            validator_comment__contains="User may not be aware so send them email reminders").distinct('subscription__contributor_profile')

        for contribution in contributions:
            print(f'Sending cart reminder to {contribution.subscription.contributor_profile.handle}')
            pending_contribution(contribution)
