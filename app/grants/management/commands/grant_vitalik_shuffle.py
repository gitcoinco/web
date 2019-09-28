# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

"""

import random

from django.core.management.base import BaseCommand

from grants.models import Grant

# VB 2019/09/27
# > To prevent a winner-takes-all effect from grants with already the most funding being shown at the top, how about a randomized sort, where your probability of being first is equal to (your expected CLR match) / (total expected CLR match) and then you just do that recursively to position everyone?


def weighted_select(ints):
    stop = random.randrange(sum(ints))
    pos = 0
    for i in ints:
        if (pos + i) > stop:
            return i
        pos += i

def weighted_shuffle(ints): 
    ints = ints[::]
    o = []
    while ints:
        o.append(weighted_select(ints))
        ints.pop(ints.index(o[-1]))
    return o

class Command(BaseCommand):

    help = 'grant weighted shuffle'

    def handle(self, *args, **options):
        grants = Grant.objects.all()
        ws = weighted_shuffle(list(range(1, grants.count()+1)))
        for grant in grants:
            grant.weighted_shuffle = ws.pop()
            grant.save()
