# -*- coding: utf-8 -*-
'''
    Copyright (C) 2017 Gitcoin Core

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

# Register your models here.
from .models import (
    EmailEvent, EmailSubscriber, GithubEvent, GithubOrgToTwitterHandleMapping, LeaderboardRank, Match, SlackPresence,
    SlackUser, Stat,
)


# Register your models here.
class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']


class EmailSubscriberAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['email', 'source']
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


admin.site.register(GithubEvent, GeneralAdmin)
admin.site.register(Match, GeneralAdmin)
admin.site.register(Stat, GeneralAdmin)
admin.site.register(EmailEvent, GeneralAdmin)
admin.site.register(EmailSubscriber, EmailSubscriberAdmin)
admin.site.register(LeaderboardRank, GeneralAdmin)
admin.site.register(SlackUser, SlackUserAdmin)
admin.site.register(SlackPresence, GeneralAdmin)
admin.site.register(GithubOrgToTwitterHandleMapping, GeneralAdmin)
