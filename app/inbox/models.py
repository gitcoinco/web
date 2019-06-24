# -*- coding: utf-8 -*-
"""Define model for the inbox app.

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
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class Notification(SuperModel):
    """Model for each notification."""

    NOTIFICATION_TYPES = (
        ('new_bounty', 'New Bounty'),
        ('start_work', 'Work Started'),
        ('stop_work', 'Work Stopped'),
        ('work_submitted', 'Work Submitted'),
        ('work_done', 'Work Done'),
        ('worker_approved', 'Worker Approved'),
        ('worker_rejected', 'Worker Rejected'),
        ('worker_applied', 'Worker Applied'),
        ('increased_bounty', 'Increased Funding'),
        ('killed_bounty', 'Canceled Bounty'),
        ('new_tip', 'New Tip'),
        ('receive_tip', 'Tip Received'),
        ('bounty_abandonment_escalation_to_mods', 'Escalated for Abandonment of Bounty'),
        ('bounty_abandonment_warning', 'Warning for Abandonment of Bounty'),
        ('bounty_removed_slashed_by_staff', 'Dinged and Removed from Bounty by Staff'),
        ('bounty_removed_by_staff', 'Removed from Bounty by Staff'),
        ('bounty_removed_by_funder', 'Removed from Bounty by Funder'),
        ('new_crowdfund', 'New Crowdfund Contribution'),
        ('new_grant', 'New Grant'),
        ('update_grant', 'Updated Grant'),
        ('killed_grant', 'Cancelled Grant'),
        ('new_grant_contribution', 'Contributed to Grant'),
        ('killed_grant_contribution', 'Cancelled Grant Contribution'),
        ('new_milestone', 'New Milestone'),
        ('update_milestone', 'Updated Milestone'),
        ('new_kudos', 'New Kudos'),
    )
    cta_url = models.URLField(max_length=500, blank=True)
    cta_text = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES
    )
    message_html = models.CharField(max_length=2000, blank=True, help_text=_("Html message"))
    is_read = models.BooleanField(default=False)
    to_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='received_notifications',
        db_index=True,
    )
    from_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )

    def __str__(self):
        return f"{self.pk} from {self.from_user} to {self.to_user}: {self.message_html}"
