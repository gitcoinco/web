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

from dashboard.models import Passport, PassportStamp

from dashboard.passport_reader import TRUSTED_IAM_ISSUER


class Command(BaseCommand):

    help = 'runs migration on the stamps table'

    def handle(self, *args, **options):
        counter = 1

        passports = Passport.objects.all()

        print(f"Migrating {passports.count()} Passports and {PassportStamp.objects.all().count()} PassportStamps\n")

        # move all stamp details in to the stamp table
        for passport in passports:
            try:
                stamps = passport.passport["stamps"]
                for stamp in stamps:
                    stamp_credential = stamp["credential"]
                    stamp_id = stamp_credential["credentialSubject"]["hash"]
                    stamp_provider = stamp_credential["credentialSubject"]["provider"]

                    # stamp_provider = f"{TRUSTED_IAM_ISSUER}#{stamp_provider}"

                    db_stamp = PassportStamp.objects.get(stamp_id=stamp_id)

                    db_stamp.stamp_provider = stamp_provider
                    db_stamp.stamp_credential = stamp_credential

                    print(f"{counter} - Saving {passport.user.profile.handle} - {stamp_id} :: {stamp_provider}")

                    db_stamp.save()

                    counter = counter+1
            except Exception as e:
                print(e)
