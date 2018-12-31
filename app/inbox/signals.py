# -*- coding: utf-8 -*-
"""Handle notification related signals.

Copyright (C) 2018 Gitcoin Core

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

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from dashboard.models import Tip
from inbox.utils import send_notification_to_user

def create_notification(sender, **kwargs):
    tip = kwargs['instance']
    if tip.txid != '':
        send_notification_to_user(
            get_user_model().objects.get(username=tip.from_username),
            get_user_model().objects.get(username=tip.username),
            tip.receive_url,
            'new_tip',
            f'<b>New Tip</b> worth {tip.value_in_usdt_now} USD '\
            f'recieved from {tip.from_username}'
        )

post_save.connect(create_notification, sender=Tip)
