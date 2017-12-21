from __future__ import print_function

import logging

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .notifications import maybe_market_to_github

logger = logging.getLogger(__name__)


def m2m_changed_interested(sender, instance, action, reverse, model, **kwargs):
    """Handle changes to Bounty interests."""
    profile_handles = []

    for profile in instance.interested.select_related('profile').all():
        profile_handles.append((profile.profile.handle, profile.profile.absolute_url))

    if action in ['post_add', 'post_remove']:
        maybe_market_to_github(instance, 'new_interest',
                               interested=profile_handles)
