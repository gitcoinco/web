# -*- coding: utf-8 -*-
"""Define util for the inbox app.

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
from django.template.defaultfilters import truncatechars

from app.utils import get_profiles_from_text
from inbox.models import Notification


def send_notification_to_user(from_user, to_user, cta_url, cta_text, msg_html):
    """Helper method to create a new notification."""
    if to_user and from_user:
      Notification.objects.create(
          cta_url=cta_url,
          cta_text=cta_text,
          message_html=msg_html,
          from_user=from_user,
          to_user=to_user
      )


def send_mention_notification_to_users(activity, mentioned_profiles):
    profile = activity.profile
    preview_post = truncatechars(activity.metadata.get('title', ''), 80)
    for mentioned_profile in mentioned_profiles:
        send_notification_to_user(cta_url=activity.url,
                                  cta_text='new_mention',
                                  msg_html=f'💬 <b>@{profile.handle} mentioned you</b> in post: "{preview_post}"',
                                  to_user=mentioned_profile.user, from_user=profile.user)


def comment_notification(comment):
    if comment.profile != comment.activity.profile:
        activity = comment.activity
        profile = comment.profile
        preview_post = truncatechars(comment.comment, 80)

        send_notification_to_user(cta_url=activity.url,
                                  cta_text='new_post_comment',
                                  msg_html=f'💬 <b>@{profile.handle} has commented</b> in your post: "{preview_post}"',
                                  to_user=activity.profile.user, from_user=profile.user)


def mentioned_users_notification(comment):
    activity = comment.activity
    profile = comment.profile
    preview_post = truncatechars(comment.comment, 80)

    mentioned_profiles = get_profiles_from_text(comment.comment).exclude(id__in=[activity.profile_id])

    for mentioned_profile in mentioned_profiles:
        send_notification_to_user(cta_url=activity.url,
                                  cta_text='new_mention',
                                  msg_html=f'💬 <b>@{profile.handle} mentioned you</b> in comment: "{preview_post}"',
                                  to_user=mentioned_profile.user, from_user=profile.user)
