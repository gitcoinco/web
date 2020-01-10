import datetime as dt
from datetime import timezone
from time import sleep

from django.core.management.base import BaseCommand

import requests
from grants.models import Contribution

start_date = dt.date(2020, 1, 5) # date to start checking

api_key = '' # add an etherscan api key here
splitter_address = '0xdf869FAD6dB91f437B59F1EdEFab319493D4C4cE'
tx_url = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={}&apikey=' + api_key
tx_list_url = 'http://api.etherscan.io/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&sort=asc&apikey=' + api_key

def verify_tx(contribution):
    r = requests.get(tx_url.format(contribution.tx_id))
    r_data = r.json().get('result')
    if not r_data:
        return None
    from_address = r_data['from']
    r_list = requests.get(tx_list_url.format(from_address))
    r_list_data = r_list.json()
    for each_tx in r_list_data['result']:
        timestamp = each_tx['timeStamp']
        tx_datetime = dt.datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        if contribution.created_on <= tx_datetime and tx_datetime <= contribution.created_on + dt.timedelta(minutes=10):
            if each_tx['to'].lower() == splitter_address.lower() and each_tx['isError'] == "1":
                print("contribution {} is suspect".format(contribution.pk))
                return contribution.pk
    return None

class Command(BaseCommand):

    help = 'checks for approval transactions followed up by failed splitter transactions'

    def handle(self, *args, **kwargs):

        contributions = Contribution.objects.filter(created_on__gt=start_date)

        suspect_contributions = []
        for c in contributions:
            print('checking {}'.format(c.pk))
            s = verify_tx(c)
            if s:
                suspect_contributions.append(s)
            sleep(0.5)

        print(suspect_contributions)
