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

from django.core.management.base import BaseCommand

# https://github.com/gitcoinco/web/issues/4424

class Command(BaseCommand):

    help = 'syncs email subscriber and profiles'

    def handle(self, *args, **options):
        from dashboard.models import Profile, SearchHistory
        from marketing.models import EmailSubscriber

        counter = 0 
        # pull keywords by search history AND emailsubscriber
        for profile in Profile.objects.filter(keywords=[]):

            histories = SearchHistory.objects.filter(user__profile=profile)
            keywords = []
            for history in histories:
                if history.data.get('keywords', None):
                    keywords = history.data['keywords'][0].split(',')

            es = EmailSubscriber.objects.filter(email=profile.email).exclude(keywords=[]).first()
            if es:
                keywords = keywords + es.keywords

            if keywords:
                print("1", counter, profile.handle, keywords)
                counter += 1
                profile.keywords = keywords
                profile.save()


        # pull keywords by profile into ES
        for es in EmailSubscriber.objects.filter(keywords=[]):
            profile = Profile.objects.filter(email=es.email).exclude(keywords=[]).first()
            if profile:
                print("2", profile.keywords, profile.handle)
                es.keywords = es.keywords + profile.keywords
                es.save()

        #TODO: if a profile / emailsubscriber both have keywords we need to merge them
