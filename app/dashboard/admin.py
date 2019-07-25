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
    Activity, BlockedUser, Bounty, BountyFulfillment, BountyInvites, BountySyncRequest, CoinRedemption,
    CoinRedemptionRequest, Coupon, FeedbackEntry, HackathonEvent, HackathonSponsor, Interest, LabsResearch, Profile,
    RefundFeeRequest, SearchHistory, Sponsor, Tip, TokenApproval, Tool, ToolVote, UserAction, UserVerificationModel,
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
    raw_id_fields = ['bounty', 'profile', 'tip', 'kudos', 'grant', 'subscription']
    search_fields = ['metadata', 'activity_type', 'profile__handle']


class TokenApprovalAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']
    search_fields = ['profile__handle', 'token_name', 'token_address']


class ToolVoteAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']


class BountyInvitesAdmin(admin.ModelAdmin):
    raw_id_fields = ['bounty']
    ordering = ['-id']


class InterestAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile']
    ordering = ['-id']
    search_fields = ['profile__handle']


class UserActionAdmin(admin.ModelAdmin):
    raw_id_fields = ['profile', 'user']
    search_fields = ['action', 'ip_address', 'metadata', 'profile__handle']
    ordering = ['-id']


class FeedbackAdmin(admin.ModelAdmin):
    search_fields = ['sender_profile','receiver_profile','bounty','feedbackType']
    ordering = ['-id']
    raw_id_fields = ['sender_profile', 'receiver_profile', 'bounty']


class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'preferred_kudos_wallet']
    ordering = ['-id']
    search_fields = ['email', 'data']
    list_display = ['handle', 'created_on']
    readonly_fields = ['active_bounties_list']

    def active_bounties_list(self, instance):
        interests = instance.active_bounties
        htmls = []
        for interest in interests:
            bounty = Bounty.objects.get(interested=interest, current_bounty=True)
            htmls.append(f"<a href='{bounty.url}'>{bounty.title_or_desc}</a>")
        html = format_html("<BR>".join(htmls))
        return html


class VerificationAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']


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
    readonly_fields = [
        'what', 'img', 'fulfillments_link', 'standard_bounties_id_link', 'bounty_link', 'network_link',
        '_action_urls', 'coupon_link'
    ]

    def img(self, instance):
        if instance.admin_override_org_logo:
            return format_html("<img src={} style='max-width:30px; max-height: 30px'>", mark_safe(instance.admin_override_org_logo.url))
        if not instance.avatar_url:
            return 'n/a'
        return format_html("<img src={} style='max-width:30px; max-height: 30px'>", mark_safe(instance.avatar_url))

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

    def _action_urls(self, instance):
        links = []
        for key, val in instance.action_urls().items():
            links.append(f"<a href={val}>{key}</a>")
        return mark_safe(", ".join(links))

    def bounty_link(self, instance):
        copy = 'link'
        url = instance.url
        return mark_safe(f"<a href={url}>{copy}</a>")

    def network_link(self, instance):
        copy = f'{instance.network}'
        url = f'/_administrationdashboard/bounty/?network={instance.network}'
        return mark_safe(f"<a href={url}>{copy}</a>")

    def coupon_link(self, instance):
        copy = f'{instance.coupon_code.code}'
        url = f'/_administrationdashboard/coupon/{instance.coupon_code.pk}'
        return mark_safe(f"<a href={url}>{copy}</a>")


class RefundFeeRequestAdmin(admin.ModelAdmin):
    """Setup the RefundFeeRequest admin results display."""

    raw_id_fields = ['bounty', 'profile']
    ordering = ['-created_on']
    list_display = ['pk', 'created_on', 'fulfilled', 'rejected', 'link', 'get_bounty_link', 'get_profile_handle',]
    readonly_fields = ['pk', 'token', 'fee_amount', 'comment', 'address', 'txnId', 'link', 'get_bounty_link',]
    search_fields = ['created_on', 'fulfilled', 'rejected', 'bounty', 'profile']

    def get_bounty_link(self, obj):
        bounty = getattr(obj, 'bounty', None)
        url = bounty.url
        return mark_safe(f"<a href={url}>{bounty}</a>")

    def get_profile_handle(self, obj):
        """Get the profile handle."""
        profile = getattr(obj, 'profile', None)
        if profile and profile.handle:
            return mark_safe(
                f'<a href=/_administration/dashboard/profile/{profile.pk}/change/>{profile.handle}</a>'
            )
        if obj.github_username:
            return obj.github_username
        return 'N/A'

    get_profile_handle.admin_order_field = 'handle'
    get_profile_handle.short_description = 'Profile Handle'

    def link(self, instance):
        """Handle refund fee request specific links.

        Args:
            instance (RefundFeeRequest): The refund request to build a link for.

        Returns:
            str: The HTML element for the refund request link.

        """
        if instance.fulfilled or instance.rejected:
            return 'n/a'
        return mark_safe(f"<a href=/_administration/process_refund_request/{instance.pk}>process me</a>")
    link.allow_tags = True


class HackathonSponsorAdmin(admin.ModelAdmin):
    """The admin object for the HackathonSponsor model."""

    list_display = ['pk', 'hackathon', 'sponsor', 'sponsor_type']


class SponsorAdmin(admin.ModelAdmin):
    """The admin object for the Sponsor model."""

    list_display = ['pk', 'name', 'img']

    def img(self, instance):
        """Returns a formatted HTML img node or 'n/a' if the HackathonEvent has no logo.

        Returns:
            str: A formatted HTML img node or 'n/a' if the HackathonEvent has no logo.
        """
        logo = instance.logo_svg or instance.logo
        if not logo:
            return 'n/a'
        img_html = format_html('<img src={} style="width: auto; max-height: 40px">', mark_safe(logo.url))
        return img_html


class HackathonEventAdmin(admin.ModelAdmin):
    """The admin object for the HackathonEvent model."""

    list_display = ['pk', 'img', 'name', 'start_date', 'end_date', 'explorer_link']
    readonly_fields = ['img', 'explorer_link']

    def img(self, instance):
        """Returns a formatted HTML img node or 'n/a' if the HackathonEvent has no logo.

        Returns:
            str: A formatted HTML img node or 'n/a' if the HackathonEvent has no logo.
        """
        logo = instance.logo_svg or instance.logo
        if not logo:
            return 'n/a'
        img_html = format_html('<img src={} style="max-width:30px; max-height: 30px">', mark_safe(logo.url))
        return img_html

    def explorer_link(self, instance):
        """Returns a formatted HTML <a> node.

        Returns:
            str: A formatted HTML <a> node.
        """

        url = f'/hackathon/{instance.slug}'
        return mark_safe(f'<a href="{url}">Explorer Link</a>')


class CouponAdmin(admin.ModelAdmin):
    """The admin object to maintain discount coupons for bounty"""

    list_display = ['pk', 'code', 'fee_percentage', 'expiry_date', 'link']
    search_fields = ['created_on', 'code', 'fee_percentage']

    def link(self, instance):
        url = f'/funding/new?coupon={instance.code}'
        return mark_safe(f'<a target="_blank" href="{url}">http://gitcoin.co{url}</a>')


admin.site.register(SearchHistory, SearchHistoryAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(BlockedUser, GeneralAdmin)
admin.site.register(UserAction, UserActionAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Bounty, BountyAdmin)
admin.site.register(BountyFulfillment, BountyFulfillmentAdmin)
admin.site.register(BountySyncRequest, GeneralAdmin)
admin.site.register(BountyInvites, BountyInvitesAdmin)
admin.site.register(Tip, TipAdmin)
admin.site.register(TokenApproval, TokenApprovalAdmin)
admin.site.register(CoinRedemption, GeneralAdmin)
admin.site.register(CoinRedemptionRequest, GeneralAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(ToolVote, ToolVoteAdmin)
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(HackathonEvent, HackathonEventAdmin)
admin.site.register(HackathonSponsor, HackathonSponsorAdmin)
admin.site.register(FeedbackEntry, FeedbackAdmin)
admin.site.register(LabsResearch)
admin.site.register(UserVerificationModel, VerificationAdmin)
admin.site.register(RefundFeeRequest, RefundFeeRequestAdmin)
admin.site.register(Coupon, CouponAdmin)
