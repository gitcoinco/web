'''
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

'''

from django.core.management.base import BaseCommand

from enssubdomain.models import ENSSubdomainRegistration


class Command(BaseCommand):

    help = 'reprocesses txs above a certain nonce'

    def add_arguments(self, parser):
        parser.add_argument('nonce', type=int, help='nonce to start above')
        parser.add_argument(
            '-clear-nonces',
            '--clear-nonces',
            action='store_true',
            dest='clear-nonces',
            default=False,
            help='Actually clear the nonces'
        )
        parser.add_argument(
            '-reprocess',
            '--reprocess',
            action='store_true',
            dest='reprocess',
            default=False,
            help='Actually reprocess the tx'
        )

    def handle(self, *args, **options):
        objs = ENSSubdomainRegistration.objects.filter(start_nonce__gte=options['nonce'])
        print(f"got {objs.count()} objs")

        if options['clear-nonces']:
            print("wiping current objects")
            for obj in objs:
                obj.start_nonce = 0
                obj.end_nonce = 0
                obj.save()

        if options['reprocess']:
            print("submitting reprocess")
            for obj in objs.exclude(profile__isnull=True).distinct('profile'):
                obj.reprocess(gas_multiplier=2)
                obj.save()
