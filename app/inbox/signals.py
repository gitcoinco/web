# -*- coding: utf-8 -*-
"""Handle notification related signals.

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

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

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
        kudos_url = reverse('profile_min', args=[
            activity.kudos_transfer.recipient_profile.handle,
            'kudos'
        ])

        if activity.kudos_transfer and activity.kudos_transfer.recipient_profile:
            kudos_url = activity.kudos_transfer.receive_url_for_recipient

        send_notification_to_user(
            activity.profile.user,
            activity.kudos_transfer.recipient_profile.user,
            kudos_url,
            'new_kudos',
            f'You received a <b>new kudos from {activity.profile.user}</b>'
        )

    if activity.activity_type == 'status_update':
        text = activity.metadata['title']
        mentioned_profiles = get_profiles_from_text(text).exclude(id__in=[activity.profile_id])
        send_mention_notification_to_users(activity, mentioned_profiles)



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
        f'❤️ <b>{like.profile.user} liked your comment</b>: {activity.metadata.get("title", "")}'
    )

@receiver(post_save, sender=Activity, dispatch_uid="psave_activitiy")
def psave_activitiy(sender, instance, created, **kwargs):
    if created:
        create_notification(sender=Activity, instance=instance)

@receiver(post_save, sender=Comment, dispatch_uid="psave_comment")
def psave_comment(sender, instance, created, **kwargs):
    if created:
        create_comment_notification(sender=Comment, instance=instance)

@receiver(post_save, sender=Like, dispatch_uid="psave_like")
def psave_like(sender, instance, created, **kwargs):
    if created:
        create_like_notification(sender=Like, instance=instance)
