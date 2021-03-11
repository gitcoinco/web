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


class Command(BaseCommand):

    help = 'patches the grants stats so that their created_on timestamps are on the hour so /grants/stats looks ok'

    def handle(self, *args, **options):
        from django.utils import timezone
        import pytz
        from grants.models import Grant
        from marketing.models import Stat

        key_titles = [
            ('_match', 'Estimated Matching Amount ($)', '-positive_round_contributor_count', 'grants' ),
            ('_pctrbs', 'Positive Contributors', '-positive_round_contributor_count', 'grants' ),
            ('_nctrbs', 'Negative Contributors', '-negative_round_contributor_count', 'grants' ),
            ('_amt', 'CrowdFund Amount', '-amount_received_in_round', 'grants' ),
            ('_admt1', 'Estimated Matching Amount (in cents) / Twitter Followers', '-positive_round_contributor_count', 'grants' ),
        ]
        keys = [ele[0] for ele in key_titles]

        key_list = []
        for key in keys:
            top_grants = Grant.objects.filter(active=True)
            grants_keys = [grant.title[0:43] for grant in top_grants]
            for grants_key in grants_keys:
                item = f"{grants_key}{key}"
                key_list.append(item)


        _from = timezone.now() - timezone.timedelta(minutes=80)
        stats = Stat.objects.filter(key__in=key_list, created_on__gt=_from).order_by('-pk')
        for stat in stats:
            stat.created_on -= timezone.timedelta(microseconds=stat.created_on.microsecond)
            stat.created_on -= timezone.timedelta(seconds=int(stat.created_on.strftime('%S')))
            stat.created_on -= timezone.timedelta(minutes=int(stat.created_on.strftime('%M')))
            stat.save()
            print(stat.pk)

        print(len(key_list), stats.count())
