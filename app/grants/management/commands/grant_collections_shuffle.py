# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

"""

import random
from datetime import datetime

from django.core.management.base import BaseCommand

from grants.models import GrantCollection

today = datetime.now()

# given the collection that was updated furthest in the past, give a higher score for collections updated more recently
# Max score increase is 5% for the newest collection
def grant_collection_age_score(oldest, current):
    currentAge = today - current.replace(tzinfo=None)
    # subtract one from ratio between current and oldest so that newest have higher chance of moving to the top
    ageScore = 1 - (currentAge / oldest)
    return int(ageScore * 500)

def grant_meta_data_score(grants):
    score = 0
    for grant in grants:

        # if grant has github url increase score by 1%
        if grant.github_project_url is not None:
            score += 100

        # Increase score by 1% for each grant that has a twitter verification
        if grant.twitter_verified:
            score += 100

    return score
        

class Command(BaseCommand):

    help = 'grant collection shuffle'

    def handle(self, *args, **options):
        oldest_creation = GrantCollection.objects.earliest()
        days_since_oldest_created = today - oldest_creation.created_on.replace(tzinfo=None)
        collections = GrantCollection.objects.filter(hidden=False)
        total = collections.count()

        print(f'No. of collections: {total}')

        # create and update the shuffle rank
        for key, gc in enumerate(collections):
            shuffle_rank = random.randint(0,999999)

            age_score = grant_collection_age_score(days_since_oldest_created, gc.created_on)
            shuffle_rank += age_score

            meta_data_score = grant_meta_data_score(gc.grants.all())
            shuffle_rank += meta_data_score


            # save the new shuffle_rank
            gc.shuffle_rank = shuffle_rank
            gc.save()

        print('done')
