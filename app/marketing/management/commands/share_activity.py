# -*- coding: utf-8 -*-
#!/usr/bin/env python3
'''
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

'''
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import twitter
from dashboard.models import Activity


class Command(BaseCommand):

    help = 'sends activity feed to twitter'

    def handle(self, *args, **options):

        api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_SECRET,
        )

        created_before = (timezone.now() - timezone.timedelta(minutes=1))
        if settings.DEBUG:
            created_before = (timezone.now() - timezone.timedelta(days=20))
        activities = Activity.objects.filter(created_on__gt=created_before)
        print(f" got {activities.count()} activities")
        for activity in activities:

            txt = activity.text

            txt = f". {txt} {activity.action_url}"

            if 'made an update to' in txt:
                continue

            try:
                print(txt)
                new_tweet = txt
                api.PostUpdate(new_tweet)
            except Exception as e:
                print(e)
