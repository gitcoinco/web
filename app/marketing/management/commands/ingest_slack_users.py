'''
    Copyright (C) 2019 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation,either version 3 of the License,or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not,see <http://www.gnu.org/licenses/>.

'''
from django.conf import settings
from django.core.management.base import BaseCommand

from marketing.utils import get_or_save_email_subscriber
from slackclient import SlackClient


class Command(BaseCommand):

    help = 'ingest slack users'

    def handle(self, *args, **options):
        sc = SlackClient(settings.SLACK_TOKEN)
        ul = sc.api_call("users.list")
        # accepted invites
        for member in ul['members']:
            try:
                email = member['profile']['email']
                get_or_save_email_subscriber(email, 'slack_ingester')
            except Exception:
                pass

        # pennding invites
        # get from https://gitcoincommunity.slack.com/admin/invites#pending
        # open chrome insepctor
        # look for 'invites' call
        # download that file, save as response.json
        # delete all lines except for the pending invites json blob
        import json
        filename = 'response.json'
        with open(filename, 'r') as f:
            members = json.load(f)
            for member in members:
                get_or_save_email_subscriber(email, 'slack_ingester')
