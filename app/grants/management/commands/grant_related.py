# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Grant


class Command(BaseCommand):

    help = 'calculate related grants'

    def handle(self, *args, **options):
        # save related addresses
        # related = same contirbutor, same cart
        grants = Grant.objects.filter(active=True).order_by('-contributor_count')
        for instance in grants:
            pk = instance.pk
            print(pk)
            related = {}
            then = timezone.now() - timezone.timedelta(days=90)
            subs = instance.subscriptions.filter(created_on__gt=then).all()
            # for perf reasons, bound this
            subs = subs[0:2000]
            for subscription in subs:
                _from = subscription.created_on - timezone.timedelta(hours=1)
                _to = subscription.created_on + timezone.timedelta(hours=1)
                profile = subscription.contributor_profile
                for _subs in profile.grant_contributor.filter(created_on__gt=_from, created_on__lt=_to).exclude(grant__id=pk):
                    key = _subs.grant.pk
                    if key not in related.keys():
                        related[key] = 0
                    related[key] += 1
            instance = Grant.objects.get(pk=pk)
            instance.metadata['related'] = sorted(related.items() ,  key=lambda x: x[1], reverse=True)
            instance.metadata['last_calc_time_related'] = time.time()
            instance.save()
