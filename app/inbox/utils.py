# -*- coding: utf-8 -*-
"""Define util for the inbox app.

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

from inbox.models import Notification


def send_notification_to_user(from_user, to_user, cta_url, cta_text, msg_html):
    """Helper method to create a new notification."""
    Notification.objects.create(
        cta_url=cta_url,
        cta_text=cta_text,
        message_html=msg_html,
        from_user=from_user,
        to_user=to_user
    )
