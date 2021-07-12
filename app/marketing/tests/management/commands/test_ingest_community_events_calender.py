# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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
import os
from unittest import mock

from icalendar import Calendar
from marketing.management.commands.ingest_community_events_calender import Command
from marketing.models import UpcomingDate
from test_plus.test import TestCase


def load_icalendar(fname):
    """ Load a iCalendar file with a single event """
    calendar = CalenderTestLoader().parse_ical_file(fname)
    event = None
    for component in calendar.walk():
        if component.name == "VEVENT":
            event = component
    return calendar, event


class CalenderTestLoader:
    """ Test iCalendar files """

    def parse_ical_file(self, fname):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), fname)) as f:
            return Calendar.from_ical(f.read())

# These Tests don't actually work - DL
class TestIngestCommunityEvents(TestCase):
    """Define tests for ingest community events. """

    def test_handle_create(self):
        """Test ingest_community_events_calender command for creating new events ."""

        calendar, event = load_icalendar("test_ics_files/single-event.ics")
        mock.patch('marketing.management.commands.ingest_community_events_calender.parse_ical_from_url',
                   lambda x: calendar).start()
        # Must create a new event
        Command().handle(url="")
        last_record = UpcomingDate.objects.last()
        assert last_record.title == event.get('summary')
        assert last_record.uid == event.get('uid')
        assert last_record.date == event.get('dtstart').dt
        assert last_record.comment == event.get('description')
        assert last_record.url == event.get('location')
        # From test_ics_files/single-event.ics:88
        assert last_record.sequence == 0
        assert last_record.last_modified == event.get('last-modified').dt

        # Case when the event already exists
        Command().handle(url="")
        assert UpcomingDate.objects.filter(title=event.get('summary')).count() == 1

    def test_handle_update(self):
        """Test ingest_community_events_calender command for updating new events ."""

        calendar, event = load_icalendar("test_ics_files/update.ics")
        mock.patch('marketing.management.commands.ingest_community_events_calender.parse_ical_from_url',
                   lambda x: calendar).start()

        # Must update the event in the test_ics_files/single-event.ics file.
        Command().handle(url="")
        last_record = UpcomingDate.objects.last()
        assert last_record.title == event.get('summary')
        assert last_record.uid == event.get('uid')
        assert last_record.date == event.get('dtstart').dt
        assert last_record.comment == event.get('description')
        assert last_record.url == event.get('location')
        # From test_ics_files/update.ics:88
        assert last_record.sequence == 1
        assert last_record.last_modified == event.get('last-modified').dt

    def tearDown(self):
        calendar, event = load_icalendar("test_ics_files/update.ics")
        UpcomingDate.objects.filter(title=event.get('summary')).delete()
