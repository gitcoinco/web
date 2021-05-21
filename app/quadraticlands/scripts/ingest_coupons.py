###
# Script is used to populate the coupon into SchwagCoupon 
# run form same directory as the csv file with something like:
# docker-compose exec web python3 app/manage.py runscript ingest_coupons.py
#
####

import csv
import os
from decimal import Decimal

from quadraticlands.models import SchwagCoupon  # imports the model

path = './app/quadraticlands'
os.chdir(path)

# SchwagCoupon.objects.all().delete() # clear the table

def ingest(path, discount_type):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                coupon = SchwagCoupon(coupon_code=row['Code'], discount_type=discount_type)
                coupon.save()
            except Exception as error:
                print(f"Unable to ingest coupon: {row['Code']}. Error: {error}")


ingest('scripts/20_off_coupons.csv', '20_off')
ingest('scripts/40_off_coupons.csv', '40_off')
ingest('scripts/60_off_coupons.csv', '60_off')

print('Coupons Ingested')

exit()
