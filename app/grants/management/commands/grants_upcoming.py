# -*- coding: utf-8 -*-
"""

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

import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Grant


class Command(BaseCommand):

    help = 'provides a upcoming_score of how up & coming a grant is + save sto db'

    def handle(self, *args, **options):

        # set default, for when no CLR match enabled
        for grant in Grant.objects.all().order_by('-clr_prediction_curve__0__1'):

            # setup
            upcoming_score = 0 # upcoming projects - weights projects that got good contributions recently
            gem_score = 0 # gem - like upcoming, but weighted more crazy heavily

            # contributions last couple hours
            upcoming_weight = 80000
            gem_weight = 6000000

            then = timezone.now() - timezone.timedelta(hours=2)
            num = grant.get_contributor_count(then, True)

            upcoming_score += num * upcoming_weight
            gem_score += num * gem_weight

            # contributions last few hours
            upcoming_weight = 80000
            gem_weight = 2000000

            then = timezone.now() - timezone.timedelta(hours=8)
            num = grant.get_contributor_count(then, True)

            upcoming_score += num * upcoming_weight
            gem_score += num * gem_weight

            # contributions last day
            upcoming_weight = 30000
            gem_weight = 500000

            then = timezone.now() - timezone.timedelta(days=1)
            num = grant.get_contributor_count(then, True)

            upcoming_score += num * upcoming_weight
            gem_score += num * gem_weight

            # contributions 3 day
            upcoming_weight = 20000
            gem_weight = 9000

            then = timezone.now() - timezone.timedelta(days=3)
            num = grant.get_contributor_count(then, True)

            upcoming_score += num * upcoming_weight
            gem_score += num * gem_weight

            # contributions last week
            upcoming_weight = 1000
            gem_weight = 1000

            then = timezone.now() - timezone.timedelta(days=7)
            num = grant.get_contributor_count(then, True)

            upcoming_score += num * upcoming_weight
            gem_score += num * gem_weight

            # contributions last month
            upcoming_weight = 500
            gem_weight = 1

            then = timezone.now() - timezone.timedelta(days=30)
            num = grant.get_contributor_count(then, True)

            upcoming_score += num * upcoming_weight
            gem_score += num * gem_weight

            # sandbag grants that already have a high match estimate
            upcoming_weight = 1800
            gem_weight = 80000

            upcoming_score += grant.clr_match_estimate_this_round * upcoming_weight * -1
            gem_score += grant.clr_match_estimate_this_round * gem_weight * -1

            # sandbag grants that have had a a lot of donations in previous rounds
            upcoming_weight = 1000
            gem_weight = 7000

            then = timezone.now() - timezone.timedelta(days=30)
            start = timezone.now() - timezone.timedelta(days=1200)
            num = grant.get_contributor_count(then, True) - grant.get_contributor_count(start, True)

            upcoming_score += grant.clr_match_estimate_this_round * upcoming_weight
            gem_score += grant.clr_match_estimate_this_round * gem_weight

            # sandbag grants that are not new
            upcoming_weight = 1000
            gem_weight = 300000

            how_old_days = (grant.created_on - timezone.now()).days

            upcoming_score += how_old_days * upcoming_weight
            gem_score += how_old_days * gem_weight

            # sandbag grants where no matching round is active
            if not grant.is_clr_active:
                upcoming_score += -100000000
                gem_score += -100000000


            # sandbag admin grants
            if grant.pk == 86:
                upcoming_score += -1000000000000
                gem_score += -1000000000000

            # save to db
            grant = Grant.objects.get(pk=grant.pk)
            grant.metadata['upcoming'] = int(upcoming_score)
            grant.metadata['gem'] = int(gem_score)
            grant.save()
            print(grant.pk)
