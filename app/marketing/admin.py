# -*- coding: utf-8 -*-
'''
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

'''
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    AccountDeletionRequest, Alumni, EmailEvent, EmailInventory, EmailSubscriber, EmailSupressionList, GithubEvent,
    GithubOrgToTwitterHandleMapping, ImageDropZone, Job, Keyword, LeaderboardRank, ManualStat, MarketingCallback, Match,
    RoundupEmail, SlackPresence, SlackUser, Stat, UpcomingDate,
)


class RoundupEmailAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']

    def response_change(self, request, obj):
        if "_send_roundup_email_myself" in request.POST:
            from marketing.tasks import weekly_roundup
            weekly_roundup.delay(request.user.profile.email)
            self.message_user(request, "Roundup Email Queued!")
        if "_send_roundup_email_everyone" in request.POST:
            from marketing.tasks import send_all_weekly_roundup
            send_all_weekly_roundup.delay()
            self.message_user(request, "Roundup Email Queued!")
        return super().response_change(request, obj)

class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']

class UpcomingDateAdmin(admin.ModelAdmin):
    ordering = ['-date']
    list_display = ['created_on', 'date', '__str__']


class LeaderboardRankAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['profile']


class EmailEventAdmin(admin.ModelAdmin):
    search_fields = ['email', 'event' ]
    ordering = ['-id']


class GithubEventAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']


class SlackPresenceAdmin(admin.ModelAdmin):
    raw_id_fields = ['slackuser']
    ordering = ['-id']


class MatchAdmin(admin.ModelAdmin):
    raw_id_fields = ['bounty']
    ordering = ['-id']


class AlumniAdmin(GeneralAdmin):
    """Define the Alumni admin layout."""

    raw_id_fields = ['profile']
    search_fields = ['organization', ]
    list_display = ['get_profile_username', 'get_profile_email', 'organization', 'created_on', ]
    readonly_fields = ['created_on', 'modified_on', ]

    def get_queryset(self, request):
        """Override the get_queryset method to include FK lookups."""
        return super(AlumniAdmin, self).get_queryset(request).select_related('profile')

    def get_profile_email(self, obj):
        """Get the profile email address."""
        return obj.profile.email

    get_profile_email.admin_order_field = 'email'
    get_profile_email.short_description = 'Profile Email'

    def get_profile_username(self, obj):
        """Get the profile username."""
        if hasattr(obj, 'profile') and obj.profile.username:
            return mark_safe(
                f'<a href=/_administrationmarketing/alumni/{obj.pk}/change/>{obj.profile.username}</a>'
            )
        elif obj.github_username:
            return obj.github_username
        return 'N/A'

    get_profile_username.admin_order_field = 'username'
    get_profile_username.short_description = 'Profile Username'


class EmailSubscriberAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']
    search_fields = ['email', 'source', 'keywords']
    list_display = ['email', 'created_on', 'source']


class SlackUserAdmin(admin.ModelAdmin):
    ordering = ['-times_seen']
    search_fields = ['email', 'username']
    list_display = ['email', 'username', 'times_seen', 'pct_seen', 'membership_length_in_days', 'last_seen']

    def pct_seen(self, instance):
        return "{}%".format(round(100 * (instance.times_seen / (instance.times_seen + instance.times_unseen))))

    def membership_length_in_days(self, instance):
        try:
            return (instance.last_seen - instance.created_on).days
        except Exception:
            return 'Unknown'


class ImageDropZoneAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['pk', 'name', 'image']


admin.site.register(MarketingCallback, GeneralAdmin)
admin.site.register(AccountDeletionRequest, GeneralAdmin)
admin.site.register(EmailSupressionList, GeneralAdmin)
admin.site.register(EmailInventory, GeneralAdmin)
admin.site.register(Alumni, AlumniAdmin)
admin.site.register(GithubEvent, GithubEventAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Job, GeneralAdmin)
admin.site.register(ManualStat, GeneralAdmin)
admin.site.register(UpcomingDate, UpcomingDateAdmin)
admin.site.register(Stat, GeneralAdmin)
admin.site.register(Keyword, GeneralAdmin)
admin.site.register(EmailEvent, EmailEventAdmin)
admin.site.register(EmailSubscriber, EmailSubscriberAdmin)
admin.site.register(LeaderboardRank, LeaderboardRankAdmin)
admin.site.register(SlackUser, SlackUserAdmin)
admin.site.register(SlackPresence, SlackPresenceAdmin)
admin.site.register(GithubOrgToTwitterHandleMapping, GeneralAdmin)
admin.site.register(RoundupEmail, RoundupEmailAdmin)
admin.site.register(ImageDropZone, ImageDropZoneAdmin)
