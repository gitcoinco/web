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
from django.db.models import Q
from django.utils import timezone

import requests
from icalendar import Calendar, Event
from marketing.models import UpcomingDate


class Command(BaseCommand):

    help = 'ingest community events calender'

    def add_arguments(self, parser):
        parser.add_argument(
                '--url',
                dest='url',
                type=str,
                default="https://calendar.google.com/calendar/ical/7rq7ga2oubv3tk93hk67agdv88%40group.calendar.google.com/public/basic.ics",
                help='The iCalendar url to ingest'
                )

    def handle(self, *args, **options):
        start_time = time.time()
        ical_content = None

        # Fetch iCalendar content from the URL
        try:
            response = requests.get(url = options['url']) 
            ical_content = response.content
        except Exception as e:
            print(e)
            return

        # Init the iCalendar object
        cal = Calendar.from_ical(ical_content)

        # Create/Update UpcomingDate objects
        updated_events = 0
        created_events = 0
        skipped_events = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                # UID field tend to be unique (ref: https://icalendar.org/iCalendar-RFC-5545/3-8-4-7-unique-identifier.html)
                uid = component.get('uid')
                # We use summary as the title field in the UpcommingDate object
                summary = component.get('summary')
                description = component.get('description')
                # This usually is a URL
                location = component.get('location')
                dtstart = component.get('dtstart')
                # Do we need to save the status field?
                status = component.get('status')
                # last_modified, sequence
                last_modified = component.get('last-modified')
                sequence = component.get('sequence')

                # Search for the record in the db
                # The Query filter could be "Q(uid=uid) | Q(title=summary)" for better accuracy, But there are some cases where the UID isn't unique! 
                # upcomming_date = UpcomingDate.objects.filter(Q(uid=uid) & Q(title=summary)).first()
                upcomming_date = UpcomingDate.objects.filter(title=summary).first()
                if upcomming_date is None:
                    # Then create an UpcommingDate object
                    UpcomingDate.objects.create(
                            uid=uid,
                            title=summary,
                            date=dtstart.dt,
                            comment=description,
                            url=location,
                            sequence=sequence,
                            last_modified=last_modified.dt,
                            )
                    created_events += 1
                # Check if we need to update the upcomming_date instance?
                elif upcomming_date.sequence < sequence or upcomming_date.last_modified < last_modified.dt:
                    # Then update all the fields
                    upcomming_date.uid=uid
                    upcomming_date.title=summary
                    upcomming_date.date=dtstart.dt
                    upcomming_date.comment=description
                    upcomming_date.url=location
                    upcomming_date.sequence=sequence
                    upcomming_date.last_modified=last_modified.dt
                    upcomming_date.save()
                    updated_events += 1
                else:
                    skipped_events += 1

        print("{} events are created".format(created_events)) 
        print("{} events are updated".format(updated_events)) 
        print("{} events are skipped".format(skipped_events)) 
        print("DONE")
