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
totals = {}

class Command(BaseCommand):

    help = 'pulls user info'

    def handle(self, *args, **options):
        total = 0
        not_found_total = 0
        outer_amount = 0
        desired_total = 14100000

        outputs = {}
        for file in csv_files:
            with open('../input/' + file) as csvfile:
                totals[file] = 0
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    try:
                        handle = row[0]
                        if handle == 'handle':
                            continue
                        pct = row[1]
                        tokens = float(row[2].replace(",",'').strip())
                        amount = int(round(tokens, round_to) * 10 ** decimals)
                        amount = amount - (amount % 10 ** 9) # handle floating arithmetic
                        if file == 'Intermediary Worksheet - KERNEL.csv':
                            amount = amount * 33.33333
                        outer_amount += amount
                        profile_id = -1
                        try:
                            profile_id = Profile.objects.get(handle=handle.lower()).pk
                        except:
                            handle = 'not_found'

                        lower_handle = handle.lower()
                        if lower_handle not in outputs.keys():
                            outputs[lower_handle] = {
                                'id': profile_id,
                            }
                        if file not in outputs[lower_handle].keys():
                            outputs[lower_handle][file] = amount
                            total += amount
                            totals[file] += amount
                            if profile_id == -1:
                                not_found_total += amount
                    except Exception as e:
                        if show_debug:
                            print("DEBUG", '------------------')
                            print("DEBUG", file)
                            print("DEBUG", handle, pct, tokens)
                            print("DEBUG", e)
        # output
        if not show_debug:
            print('handle,user_id,total,active_user,kernel,GMV')
            for key, bundle in outputs.items():
                _id = bundle['id']
                gmv = bundle.get('Intermediary Worksheet - GMV.csv', 0)
                au = bundle.get('Intermediary Worksheet - Active Users.csv', 0)
                kernel = bundle.get('Intermediary Worksheet - KERNEL.csv', 0)
                total = kernel + au + gmv
                print(f"{key},{_id},{total},{au},{kernel},{gmv}")
        else:
            print(f"outer_amount: {round(outer_amount/10**18)}")
            print(f"total: {round(total/10**18)}")
            print(f"not_found_total: {round(not_found_total/10**18)}")
            for key, val in totals.items():
                print(f"- {key}: {round(val/10**18)}")
            print("=========================")
            print(f"desired_total: {round(desired_total)}")
            print("goals GMV - 10,800,000")
            print("goals KERNEL - 240,000")
            print("goals AU - 3,060,000")
            print("goals FL - 900,000")


