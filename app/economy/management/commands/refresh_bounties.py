# -*- coding: utf-8 -*-
"""Define the management command to refresh bounty data.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import time

from django.core.management.base import BaseCommand

from dashboard.models import Bounty


class Command(BaseCommand):
    """Define the management command to refresh bounties."""

    help = 'refreshes the triggers associated with current bounties'

    def add_arguments(self, parser):
        """Add argument handling to the refresh command."""
        parser.add_argument(
            '-r', '--remote',
            action='store_true',
            dest='remote',
            default=False,
            help='Pulls remote info about bounty too'
        )

    def handle(self, *args, **options):
        """Refresh all bounties.

        Attributes:
            all_bounties (QuerySet of Bounty): The queryset of all Bounties.
            fetch_remote (bool): Whether or not to fetch remote bounties.
                Defaults to: `False` unless user passes the remote option.

        """
        all_bounties = Bounty.objects.filter(current_bounty=True).order_by('-pk')
        fetch_remote = options['remote']
        print(f"refreshing {all_bounties.count()} bounties")

        for bounty in all_bounties:

            # IMPORTANT -- if you change the criteria for deriving old_bounties
            # make sure it is updated in dashboard.helpers/bounty_did_change
            # AND
            # refresh_bounties/handle
            # stopgap to make sure that older versions of this bounty
            # are marked as current_bounty=False
            try:
                if fetch_remote:
                    bounty.fetch_issue_item('title')
                    bounty.fetch_issue_item()
                    bounty.fetch_issue_comments()
                    time.sleep(10)
                    print('1/ refreshed', bounty.pk)
            except Exception as e:
                print(e)

            bounty.save()
