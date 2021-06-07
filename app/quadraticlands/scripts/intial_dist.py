###
# Script is used to populate the initial token distribution in the DB
# run form same directory as the initial_dist.csv file with something like:
# docker-compose exec web python3 app/manage.py runscript initial_dist.py
#
####
# from quadraticlands.models import InitialTokenDistribution
# from dashboard.models import Profile
import csv
import os
from decimal import Decimal

from dashboard.models import Profile  # import profile model
from quadraticlands.models import InitialTokenDistribution  # imports the model

path = './app/quadraticlands'
os.chdir(path)

InitialTokenDistribution.objects.all().delete() # clear the table

with open('scripts/initial_dist.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            # grab the user_id and amount
            user_id = int(row['user_id'])
            amount_in_wei = Decimal(row['total'])
            dist = {
                "active_user": row['active_user'],
                "kernel": row['kernel'],
                "GMV": row['GMV']
            }
            # get the profile for this user_id
            p = Profile.objects.get(id=user_id)
            # create the record
            c = InitialTokenDistribution(profile=p, claim_total=amount_in_wei, distribution=dist) # create initial dist record
            # save record
            c.save()
        except Exception as error:
            print(f"User: {row['handle']} - {row['user_id']} was not added. Error: {error}")
exit()
