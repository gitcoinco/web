'''
    Copyright (C) 2019 Gitcoin Core

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

from dashboard.views import w3
from marketing.mails import warn_account_out_of_eth


class Command(BaseCommand):

    help = 'warns the admins when any of the monitored_accounts is out of gas'

    def handle(self, *args, **options):
        monitored_accounts = [settings.ENS_OWNER_ACCOUNT, settings.KUDOS_OWNER_ACCOUNT, settings.GRANTS_OWNER_ACCOUNT]
        for account in monitored_accounts:
            balance_eth_threshold = 0.07

            balance_wei = w3.eth.getBalance(account)
            balance_eth = balance_wei / 10**18

            if balance_eth < balance_eth_threshold:
                warn_account_out_of_eth(account, balance_eth, 'ETH')
