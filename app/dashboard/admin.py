'''
    Copyright (C) 2019 Gitcoin Core

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
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Activity, BlockedUser, Bounty, BountyFulfillment, BountySyncRequest, CoinRedemption, CoinRedemptionRequest,
    Interest, LabsResearch, Profile, SearchHistory, Tip, TokenApproval, Tool, ToolVote, UserAction,
)


class BountyFulfillmentAdmin(admin.ModelAdmin):
    raw_id_fields = ['bounty', 'profile']
    search_fields = ['fulfiller_address', 'fulfiller_email', 'fulfiller_github_username',
                     'fulfiller_name', 'fulfiller_metadata', 'fulfiller_github_url']
    ordering = ['-id']


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']


class ToolAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['votes']


class ActivityAdmin(admin.ModelAdmin):
    ordering = ['-id']
    raw_id_fields = ['bounty', 'profile', 'tip', 'kudos']
    search_fields = ['metadata', 'activity_type', 'profile__handle']


class TokenApprovalAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']
    search_fields = ['profile__handle', 'token_name', 'token_address']


class ToolVoteAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']


class InterestAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']
    search_fields = ['profile__handle']


class UserActionAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile', 'user']
    search_fields = ['action', 'ip_address', 'metadata', 'profile__handle']
    ordering = ['-id']


class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'preferred_kudos_wallet']
    ordering = ['-id']
    search_fields = ['email', 'data']
    list_display = ['handle', 'created_on']


class SearchHistoryAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    ordering = ['-id']
    search_fields = ['user', 'data']
    list_display = ['user', 'data']


class TipAdmin(admin.ModelAdmin):
    raw_id_fields = ['recipient_profile', 'sender_profile']
    ordering = ['-id']
    readonly_fields = ['resend', 'claim']
    search_fields = [
        'tokenName', 'comments_public', 'comments_priv', 'from_name', 'username', 'network', 'github_url', 'url',
        'emails', 'from_address', 'receive_address', 'ip', 'metadata', 'txid', 'receive_txid'
    ]

    def resend(self, instance):
        html = format_html('<a href="/_administration/email/new_tip/resend?pk={}">resend</a>', instance.pk)
        return html

    def claim(self, instance):
        if instance.web3_type == 'yge':
            return 'n/a'
        if not instance.txid:
            return 'n/a'
        if instance.receive_txid:
            return 'n/a'
        try:
            if instance.web3_type == 'v2':
                html = format_html('<a href="{}">claim</a>', instance.receive_url)
            if instance.web3_type == 'v3':
                html = format_html(f'<a href="{instance.receive_url_for_recipient}">claim as recipient</a>')
        except Exception:
            html = 'n/a'
        return html


# Register your models here.
class BountyAdmin(admin.ModelAdmin):
    raw_id_fields = ['interested', 'bounty_owner_profile', 'bounty_reserved_for_user']
    ordering = ['-id']

    search_fields = ['raw_data', 'title', 'bounty_owner_github_username', 'token_name']
    list_display = ['pk', 'img', 'idx_status', 'network_link', 'standard_bounties_id_link', 'bounty_link', 'what']
    readonly_fields = ['what', 'img', 'fulfillments_link', 'standard_bounties_id_link', 'bounty_link', 'network_link', 'contract_version']

    def img(self, instance):
        if not instance.avatar_url:
            return 'n/a'
        img_html = format_html("<img src={} style='max-width:30px; max-height: 30px'>", mark_safe(instance.avatar_url))
        return img_html

    def what(self, instance):
        return str(instance)

    def fulfillments_link(self, instance):
        copy = f'fulfillments({instance.num_fulfillments})'
        url = f'/_administrationdashboard/bountyfulfillment/?bounty={instance.pk}'
        return mark_safe(f"<a href={url}>{copy}</a>")

    def standard_bounties_id_link(self, instance):
        copy = f'{instance.standard_bounties_id}'
        url = f'/_administrationdashboard/bounty/?standard_bounties_id={instance.standard_bounties_id}'
        return mark_safe(f"<a href={url}>{copy}</a>")

    def bounty_link(self, instance):
        copy = 'link'
        url = instance.url
        return mark_safe(f"<a href={url}>{copy}</a>")

    def network_link(self, instance):
        copy = f'{instance.network}'
        url = f'/_administrationdashboard/bounty/?network={instance.network}'
        return mark_safe(f"<a href={url}>{copy}</a>")

    def contract_version(self, instance):
        return str(instance.contract_version)


admin.site.register(SearchHistory, SearchHistoryAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(BlockedUser, GeneralAdmin)
admin.site.register(UserAction, UserActionAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Bounty, BountyAdmin)
admin.site.register(BountyFulfillment, BountyFulfillmentAdmin)
admin.site.register(BountySyncRequest, GeneralAdmin)
admin.site.register(Tip, TipAdmin)
admin.site.register(TokenApproval, TokenApprovalAdmin)
admin.site.register(CoinRedemption, GeneralAdmin)
admin.site.register(CoinRedemptionRequest, GeneralAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(ToolVote, ToolVoteAdmin)
admin.site.register(LabsResearch)
