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

from app.utils import get_default_network

from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Contribution, Grant, Subscription
from grants.tasks import process_new_contributions_email


class Command(BaseCommand):

    help = 'send contribution summary emails to grant owners'

    def handle(self, *args, **options):
        network = get_default_network()
        grant_ids = Contribution.objects.filter(
            created_on__gt=timezone.now() - timezone.timedelta(hours=12),
            subscription__network=network,
            success=True
        ).values_list('normalized_data__id', flat=True).distinct()

        for grant_id in grant_ids:
            process_new_contributions_email(grant_id)
