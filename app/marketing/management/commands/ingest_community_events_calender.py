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
import time

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

import requests
from icalendar import Calendar, Event
from marketing.models import UpcomingDate

# The iCal link for Gitcoin community events calender
ICAL_URL = "https://calendar.google.com/calendar/ical/7rq7ga2oubv3tk93hk67agdv88%40group.calendar.google.com/public/basic.ics"


def parse_ical_from_url(url: str):
    """ Fetch iCalendar content from the URL """
    ical_content = None
    try:
        response = requests.get(url=url)
        ical_content = response.content
    except Exception as e:
        raise(e)
    # Init the iCalendar object
    return Calendar.from_ical(ical_content)


def save_upcoming_date(component):
    """ Create an UpcomingDate record or Update existing record if the event already exist in the db.

        :type component:Event

        :rtype: (int, int, int) The tuple of created, updated, skipped 
    """
    # UID field tend to be unique (ref: https://icalendar.org/iCalendar-RFC-5545/3-8-4-7-unique-identifier.html)
    uid = component.get('uid')
    # We use summary as the title field in the UpcomingDate object
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
    # upcoming_date = UpcomingDate.objects.filter(Q(uid=uid) & Q(title=summary)).first()
    upcoming_date = UpcomingDate.objects.filter(title=summary).first()
    if upcoming_date is None:
        # Then create an UpcomingDate object
        UpcomingDate.objects.create(
            uid=uid,
            title=summary,
            date=dtstart.dt,
            comment=description,
            url=location,
            sequence=sequence,
            last_modified=last_modified.dt,
        )
        return 1, 0, 0
    # Check if we need to update the upcoming_date instance?
    elif upcoming_date.sequence < sequence or upcoming_date.last_modified < last_modified.dt:
        # Then update all the fields
        upcoming_date.uid = uid
        upcoming_date.title = summary
        upcoming_date.date = dtstart.dt
        upcoming_date.comment = description
        upcoming_date.url = location
        upcoming_date.sequence = sequence
        upcoming_date.last_modified = last_modified.dt
        upcoming_date.save()
        return 0, 1, 0
    else:
        return 0, 0, 1

class Command(BaseCommand):

    help = 'ingest community events calender'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            dest='url',
            type=str,
            default=ICAL_URL,
            help='The iCalendar url to ingest'
        )

    def handle(self, *args, **options):
        # Init the iCalendar object
        cal = parse_ical_from_url(options['url'])

        # Create/Update UpcomingDate objects
        updated_events = 0
        created_events = 0
        skipped_events = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                (created, updated, skipped) = save_upcoming_date(component)
                created_events += created
                updated_events += updated
                skipped_events += skipped

        print("{} events are created".format(created_events))
        print("{} events are updated".format(updated_events))
        print("{} events are skipped".format(skipped_events))
        print("DONE")
