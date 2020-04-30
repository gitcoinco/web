'''
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

'''

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from dashboard.models import Profile


class Command(BaseCommand):

    help = 'update failed + successfull authorization'

    def handle(self, *args, **options):
        try:

            headers = {
                "Authorization": settings.PASSBASE_SECRET_API_KEY,
                "Accept":"application/json"
            }

            unverified_profiles = Profile.objects.filter(kyc_status__in=[0])

            # failed verifications
            url = "https://api.passbase.com/api/v1/authentications?offset=1"
            response = requests.get(url = url, headers = headers).json()
            pending_authentications = response['authentications']

            for authentication in pending_authentications:
                pk = (int)(authentication['additional_attributes']['customer_user_id'])
                profile = unverified_profiles.filter(pk=pk)
                if profile:
                    profile.kyc_status = 1
                    profile.save()

            # successfull verifications
            url = "https://api.passbase.com/api/v1/authentications?offset=2"
            response = requests.get(url = url, headers = headers).json()
            pending_authentications = response['authentications']

            for authentication in pending_authentications:
                pk = (int)(authentication['additional_attributes']['customer_user_id'])
                profile = unverified_profiles.filter(pk=pk)
                if profile:
                    profile.kyc_status = 2
                    profile.save()

        except Exception as e:
            print(f'error running sync_passbase - {e}')
