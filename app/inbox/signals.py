# -*- coding: utf-8 -*-
"""Handle notification related signals.

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
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from app.utils import get_profiles_from_text
from dashboard.models import Activity
from inbox.utils import (
    comment_notification, mentioned_users_notification, send_mention_notification_to_users, send_notification_to_user,
)
from townsquare.models import Comment, Like


def create_notification(sender, **kwargs):
    activity = kwargs['instance']
    if activity.activity_type == 'new_tip':
        tip = activity.tip
        if tip.recipient_profile:
            send_notification_to_user(
                activity.profile.user,
                tip.recipient_profile.user,
                tip.receive_url,
                'new_tip',
                f'<b>New Tip</b> worth {tip.value_in_usdt_now} USD ' +
                f'recieved from {tip.from_username}'
            )

    if activity.activity_type == 'worker_applied':
        bounty = activity.bounty
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'worker_applied',
            f'<b>{activity.profile.user} applied</b> to work on {bounty.title}'
        )

    if activity.activity_type == 'worker_approved':
        bounty = activity.bounty
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=activity.metadata['worker_handle']),
            bounty.url,
            'worker_approved',
            f'You have been <b>approved to work on {bounty.title}</b>'
        )

    if activity.activity_type == 'worker_rejected':
        bounty = activity.bounty
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=activity.metadata['worker_handle']),
            bounty.url,
            'worker_rejected',
            f'Your request to work on <b>{bounty.title} has been rejected</b>'
        )

    if activity.activity_type == 'start_work':
        bounty = activity.bounty
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'start_work',
            f'<b>{activity.profile.user} has started work</b> on {bounty.title}'
        )

    if activity.activity_type == 'work_submitted':
        bounty = activity.bounty
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'work_submitted',
            f'<b>{activity.profile.user} has submitted work</b> for {bounty.title}'
        )

    if activity.activity_type == 'work_done':
        bounty = activity.bounty
        amount_paid = activity.metadata['new_bounty']['value_in_usdt_now']
        send_notification_to_user(
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            activity.profile.user,
            bounty.url,
            'work_done',
            f'<b>{bounty.bounty_owner_github_username}</b> has paid out ' +
            f'{amount_paid} USD for your work on {bounty.title}'
        )

    if activity.activity_type == 'stop_work':
        bounty = activity.bounty
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'stop_work',
            f'<b>{activity.profile.user} has stopped work</b> on {bounty.title}'
        )

    if activity.activity_type == 'new_crowdfund':
        bounty = activity.bounty
        amount = activity.metadata['value_in_usdt_now']
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'new_crowdfund',
            f'A <b>crowdfunding contribution worth {amount} USD</b> has been attached for {bounty.title}'
        )

    if activity.activity_type == 'new_kudos':
        send_notification_to_user(
            activity.profile.user,
            activity.kudos_transfer.recipient_profile.user,
            activity.kudos_transfer.receive_url_for_recipient,
            'new_kudos',
            f'You received a <b>new kudos from {activity.profile.user}</b>'
        )

    if activity.activity_type == 'funder_none_response_in_issue':
        bounty = activity.bounty
        message = """Your bounty hunters haven't responded on this issue
         in a few days. Remove them if you haven't heard from them?"""
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'funder_none_response_in_issue',
            message
        )

    if activity.activity_type == 'funder_bounty_expiring':
        bounty = activity.bounty
        message = 'Your bounty is expiring soon.'
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'funder_bounty_expiring',
            message
        )


    if activity.activity_type == 'hunter_none_response':
        bounty = activity.bounty
        days_without_response = activity.metadata['days_without_response']
        message = f'You haven\'t responded to this issue in {days_without_response} days.'
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'hunter_none_response',
            message
        )

    if activity.activity_type == 'hunter_has_the_right_skills':
        bounty = activity.bounty
        message = """This issue has been remarketed and has your skill sets.
         Are you interested?"""
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'hunter_has_the_right_skills',
            message
        )

    if activity.activity_type == 'hunter_removed_from_bounty':
        bounty = activity.bounty
        message = 'You have been removed from a bounty due to no response'
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'hunter_removed_from_bounty',
            message
        )

    if activity.activity_type == 'hunter_submission_declined':
        bounty = activity.bounty
        message = 'Your submission has been declined.'
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'hunter_submission_declined',
            message
        )

    if activity.activity_type == 'hunter_issue_funding_increased':
        bounty = activity.bounty
        message = 'Funding has increased on a bounty that you’re working on.'
        send_notification_to_user(
            activity.profile.user,
            get_user_model().objects.get(username__iexact=bounty.bounty_owner_github_username),
            bounty.url,
            'hunter_issue_funding_increased',
            message
        )


# Added due comments and likes aren't direct members of activity.
# So new likes and comments doesn't trigger the Activity post_save
def create_comment_notification(sender, **kwargs):
    comment = kwargs['instance']
    comment_notification(comment)
    mentioned_users_notification(comment)


def create_like_notification(sender, **kwargs):
    like = kwargs['instance']
    activity = like.activity
    if activity.profile_id == like.profile_id:
        return

    send_notification_to_user(
        like.profile.user,
        activity.profile.user,
        activity.url,
        'new_like',
        f'❤️ <b>{like.profile.user} liked your comment</b>: {activity.metadata["title"]}'
    )


post_save.connect(create_notification, sender=Activity)
post_save.connect(create_comment_notification, sender=Comment)
post_save.connect(create_like_notification, sender=Like)
