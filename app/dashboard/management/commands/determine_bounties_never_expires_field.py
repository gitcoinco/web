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

from dashboard.models import Bounty

class Command(BaseCommand):

    help = """This will set the `never_expire` flag to true on each bounty that meets the following criteria:
        - never_expire - is false
        - expires_date - is far into the future (year > 2200)

    """

    def add_arguments(self , parser):
        parser.add_argument('--exec', action='store_true')

    def handle(self, *args, **options):
        do_exec = options["exec"]
        if not do_exec:
            print("""
****************************************************************************************
* This is a dry run, no processes will be killed
* In order to kill the processes re-run this command with the '--exec' option
****************************************************************************************
""")

        bounties = Bounty.objects.all()

        for bounty in bounties:
            print("checkin bounty -- date: %s, never_expires=%s bounty summary: %s" % (bounty.expires_date, bounty.never_expires, bounty))
            if bounty.expires_date.year > 2200 and not bounty.never_expires:
                print("     -> setting never_expires flag to True")

                if do_exec:
                    bounty.never_expires = True
                    bounty.save()
