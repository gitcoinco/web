'''
    Copyright (C) 2020 Gitcoin Core

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

import math
import random
import time

from django.core.management.base import BaseCommand
from instant.models import Clients


class Command(BaseCommand):

    help = 'sends a test message to every channel a user is in'

    def handle(self, *args, **options):

        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        announcement_text = 'owocki forever'
        channel_layer = get_channel_layer()

        # send to individual channels using DB info
        chats = Clients.objects.filter(user__username='owocki').values_list('channel_name', flat=True)
        for chat_name in chats:
            if False:
                async_to_sync(channel_layer.send)(chat_name, {"type" : 'chat_message', "message": announcement_text})

        # send to channel group
        async_to_sync(channel_layer.group_send)('chat', {"type" : 'chat_message', "message": announcement_text})
