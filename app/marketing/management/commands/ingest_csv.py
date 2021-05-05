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
import time
import warnings
import csv

show_debug = False
from django.core.management.base import BaseCommand

from dashboard.models import Profile

csv_files = [
    'Intermediary Worksheet - GMV.csv',
    'Intermediary Worksheet - Active Users.csv',
    'Intermediary Worksheet - KERNEL.csv',
]
decimals = 18
round_to = 4

class Command(BaseCommand):

    help = 'pulls user info'

    def handle(self, *args, **options):
        outputs = {}
        for file in csv_files:
            with open('../input/' + file) as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    try:
                        handle = row[0]
                        if handle == 'handle':
                            continue
                        pct = row[1]
                        tokens = float(row[2].replace(",",''))
                        profile_id = Profile.objects.get(handle=handle.lower()).pk

                        lower_handle = handle.lower()
                        if lower_handle not in outputs.keys():
                            outputs[lower_handle] = {
                                'id': profile_id,
                            }
                        if file not in outputs[lower_handle].keys():
                            amount = int(round(tokens, round_to) * 10 ** decimals)
                            amount = amount - (amount % 10 ** 9) # handle floating arithmetic
                            outputs[lower_handle][file] = amount
                    except Exception as e:
                        if show_debug:
                            print('------------------')
                            print(file)
                            print(handle, pct, tokens)
                            print(e)
        # output
        # handle,user_id,total,active_user,kernel,GMV
        print('handle,user_id,total,active_user,kernel,GMV')
        for key, bundle in outputs.items():
            _id = bundle['id']
            gmv = bundle.get('Intermediary Worksheet - GMV.csv', 0)
            au = bundle.get('Intermediary Worksheet - Active Users.csv', 0)
            kernel = bundle.get('Intermediary Worksheet - KERNEL.csv', 0)
            total = kernel + au + gmv
            print(f"{key},{_id},{total},{au},{kernel},{gmv}")

