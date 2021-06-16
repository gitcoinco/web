###
# Script is used to populate the stewards into GTCSteward 
# run form same directory as the csv file with something like:
# docker-compose exec web python3 app/manage.py runscript ingest_steward.py
#
####

import csv
import os
from decimal import Decimal
from urllib.request import urlopen

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from dashboard.models import Profile
from quadraticlands.models import GTCSteward  # imports the model

path = './app/quadraticlands'
os.chdir(path)

GTCSteward.objects.all().delete() # clear the table

def ingest(path):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                image_url = row['image']
                img_temp = NamedTemporaryFile(delete = True)
                img_temp.write(urlopen(image_url).read())
                img_temp.flush()


                handle=row['handle']
                profile = Profile.objects.get(handle=handle)
                steward = GTCSteward(
                    profile=profile,
                    real_name=row['real_name'],
                    bio=row['bio'],
                    gtc_address=row['gtc_address'],
                    profile_link=row['profile_link'],
                    custom_steward_img = File(img_temp)
                )
                steward.save()
            except Exception as error:
                print(f"Unable to ingest steward: {row['handle']}. Error: {error}")


ingest('scripts/stewards.csv')


print('Stewards Ingested')

exit()
