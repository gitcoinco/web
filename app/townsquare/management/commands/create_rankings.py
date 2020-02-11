'''
    Copyright (C) 2020 Gitcoin Core

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

from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone
from townsquare.models import MatchRound, MatchRanking
from django.db import transaction
from dashboard.models import Earning, Profile
import townsquare.clr as clr
from django.conf import settings

def get_eligible_input_data(mr):
    earnings = Earning.objects.filter(created_on__gt=mr.valid_from, created_on__lt=mr.valid_to)
    earnings = earnings.filter(to_profile__isnull=False, from_profile__isnull=False, value_usd__isnull=False)
    earnings = earnings.values_list('to_profile__pk', 'from_profile__pk', 'value_usd')
    return [[ele[0], ele[1], float(ele[2])] for ele in earnings]

class Command(BaseCommand):

    help = 'creates round rankings'

    def handle(self, *args, **options):
        mr = MatchRound.objects.current().first()
        with transaction.atomic():
            mr.ranking.all().delete()
            data = get_eligible_input_data(mr)
            total_pot = mr.amount
            print(mr, f"{len(data)} earnings to process")
            results = clr.run_calc(data, total_pot)
            for result in results:
                try:
                    profile = Profile.objects.get(pk=result['id'])
                    contributions_by_this_user = [ele for ele in data if int(ele[0]) == profile.pk]
                    contributions = len(contributions_by_this_user)
                    contributions_total = sum([ele[2] for ele in contributions_by_this_user])
                    MatchRanking.objects.create(
                        profile=profile,
                        round=mr,
                        contributions=contributions,
                        contributions_total=contributions_total,
                        match_total=result['clr_amount'],
                        )
                except Exception as e:
                    if settings.DEBUG:
                        raise e

            # update number rankings
            number = 1
            for mri in mr.ranking.order_by('-match_total'):
                mri.number = number
                mri.save()
                number += 1

