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

from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from townsquare.models import MatchRound


class Command(BaseCommand):

    help = 'creates mini match rounds'

    def add_arguments(self, parser):
        parser.add_argument(
            'rounds',
            default=1,
            type=int,
            help="The number of rounds to schedule"
        )
        parser.add_argument(
            'days',
            default=14,
            type=int,
            help="The number of days to schedule this for"
        )
        parser.add_argument(
            'amount',
            default=200,
            type=int,
            help="Amount in USD for the round"
        )


    def handle(self, *args, **options):
        for i in range(0, options['amount']):
            last_round = MatchRound.objects.order_by('-valid_from').first()
            MatchRound.objects.create(
                valid_from = last_round.valid_to,
                valid_to = last_round.valid_to + timezone.timedelta(days=options['days']),
                amount = options['amount'],
                number = last_round.number + 1,
                )
