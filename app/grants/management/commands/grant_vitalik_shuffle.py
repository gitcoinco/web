# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

"""

import random

from django.core.management.base import BaseCommand

from grants.models import Grant, GrantCLR

# VB 2019/09/27
# > To prevent a winner-takes-all effect from grants with already the most funding being shown at the top, how about a randomized sort, where your probability of being first is equal to (your expected CLR match) / (total expected CLR match) and then you just do that recursively to position everyone?


def weighted_select(items):
    stop = random.randrange(sum([ele[1] for ele in items]))
    pos = 0
    for ele in items:
        i = ele[1]
        if (pos + i) > stop:
            return i
        pos += i

def custom_index(arr, item):
    for i in range(0, len(arr)):
        if arr[i][1] == item:
            return i

def weighted_shuffle(items):
    o = []
    while items:
        o.append(weighted_select(items))
        items.pop(custom_index(items, o[-1]))
    return o

class Command(BaseCommand):

    help = 'grant weighted shuffle'

    def handle(self, *args, **options):

        active_clr_rounds =  GrantCLR.objects.filter(is_active=True)
        if active_clr_rounds.count() == 0:
            return

        # TODO-SELF-SERVICE: Check if it's alright to shuffle all grants even if 1 CLR round is active

        # set default, for when no CLR match enabled
        for grant in Grant.objects.all():
            grant.weighted_shuffle = 99999
            grant.save()

        # get grants, and apply weighted shuffle rank to them
        grants = Grant.objects.filter(clr_prediction_curve__0__1__isnull=False, is_clr_active=True).order_by('pk')
        weighted_list = [(grant, int(max(1, grant.clr_prediction_curve[0][1]))) for grant in grants]
        og_weighted_list = weighted_list.copy()
        ws = weighted_shuffle(weighted_list)
        counter = 0

        # update grants in db
        for ele in ws:
            grant_idx = custom_index(og_weighted_list, ele)
            grant = grants[grant_idx]
            grant.weighted_shuffle = counter
            grant.save()
            counter+=1
