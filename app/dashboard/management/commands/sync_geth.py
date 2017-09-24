'''
    Copyright (C) 2017 Gitcoin Core 

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

'''
from django.core.management.base import BaseCommand
from django.conf import settings
from economy.eth import getWeb3, getBountyContract, get_network_details
from django.utils import timezone
from dashboard.helpers import syncBountywithWeb3, process_bounty_changes, normalizeURL
from dashboard.models import BountySyncRequest
import time
import requests

POLL_SLEEP_TIME = 3


def get_callback(web3, bounty_contract_address, realtime):

    def process_change(bountyContract, url, txid):
        url = normalizeURL(url)
        didChange, old_bounty, new_bounty = syncBountywithWeb3(bountyContract, url)
        print("{} changed, {}".format(didChange, url))
        if didChange:
            print("- processing changes");
            process_bounty_changes(old_bounty, new_bounty, txid)

    def realtime_callback(transaction_hash):
        block = web3.eth.getBlock('latest')
        fromBlock = block['number'] - 1
        _filter = web3.eth.filter({
            "fromBlock": fromBlock,
            "toBlock": "latest",
            "address": bounty_contract_address,
        })
        bountyContract = getBountyContract(web3, bounty_contract_address)

        log_entries = _filter.get(False)
        print('got {} log entrires from web3'.format(len(log_entries)))

        for entry in log_entries:
            txid = entry['transactionHash']
            result = web3.toAscii(entry['data']);
            result = result[result.find('http'):]
            url = result[:result.find('\x00')]
            process_change(bountyContract, url, txid)

    def faux_realtime_callback(block_id):
        bountyContract = getBountyContract(web3, bounty_contract_address)
        bsrs = BountySyncRequest.objects.filter(processed=False)

        for bsr in bsrs:
            url = bsr.github_url
            process_change(bountyContract, url, None)

        pass

    return realtime_callback if realtime else faux_realtime_callback


class Command(BaseCommand):

    help = 'syncs bounties with geth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--network',
            dest='network',
            type=str,
            default=settings.DEFAULT_NETWORK,
            help="network (optional)",
        )

        parser.add_argument(
            '--provider',
            dest='provider',
            type=str,
            default='default',
            help="provider (optional)",
        )

    def handle(self, *args, **options):

        # setup
        bounty_contract_address, infura_host, custom_geth_details, is_testnet = get_network_details(options['network'])
        print("****************************************")
        print("connecting {} {} ....".format(options['network'], options['provider']))
        print("****************************************")

        start_time = int(timezone.now().strftime("%S"))
        web3 = getWeb3(options['network'], options['provider'])
        end_time = int(timezone.now().strftime("%S"))
        connect_time = end_time - start_time
        
        print("****************************************")
        print("connected to {} (took {} s)".format(web3.currentProvider.__class__, connect_time))
        print("****************************************")

        # get past event topics
        try:
            print('- attempting realtime')
            callback = get_callback(web3, bounty_contract_address, True)
            web3.eth.filter('pending').watch(callback)
            print('- sleeping')
            while True:
                time.sleep(1)
        except requests.exceptions.HTTPError:
            print("- realtime not working.  attempting to faux realtime! #YOLO")
            callback = get_callback(web3, bounty_contract_address, False)
            last_blockNumber = 0
            while True:
                blockNumber = web3.eth.blockNumber
                if blockNumber != last_blockNumber:
                    print("-- new block: {}".format(blockNumber))
                    callback(blockNumber) 
                last_blockNumber = blockNumber
                time.sleep(POLL_SLEEP_TIME)


