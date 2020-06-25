# -*- coding: utf-8 -*-
"""Define the Grant admin layout.

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
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from grants.models import CartActivity, CLRMatch, Contribution, Flag, Grant, MatchPledge, PhantomFunding, Subscription


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


class FlagAdmin(admin.ModelAdmin):
    """Define the FlagAdmin administration layout."""

    ordering = ['-id']
    raw_id_fields = ['profile', 'grant']

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_post_flag" in request.POST:
            obj.post_flag()
            self.message_user(request, "posted flag to activity feed")
        if "_tweet" in request.POST:
            import twitter
            from django.conf import settings
            # TODO : get @gicoindisputes out of twitter jail
            api = twitter.Api(
                consumer_key=settings.DISPUTES_TWITTER_CONSUMER_KEY,
                consumer_secret=settings.DISPUTES_TWITTER_CONSUMER_SECRET,
                access_token_key=settings.DISPUTES_TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.DISPUTES_TWITTER_ACCESS_SECRET,
            )
            new_tweet = f"{settings.BASE_URL}{obj.grant.url} : {obj.comments}"[0:280]
            result = api.PostUpdate(new_tweet).AsDict()
            obj.processed = True
            obj.tweet = f"https://twitter.com/{result['user']['screen_name']}/statuses/{result['id']}"
            obj.save()
            self.message_user(request, "posted flag to twitter feed")
        return redirect(obj.admin_url)



class MatchPledgeAdmin(admin.ModelAdmin):
    """Define the MatchPledge administration layout."""

    ordering = ['-id']
    raw_id_fields = ['profile']
    list_display =['pk', 'profile', 'active','pledge_type','amount']


class CLRMatchAdmin(admin.ModelAdmin):
    """Define the CLRMatch administration layout."""

    ordering = ['-id']
    raw_id_fields = ['grant', 'payout_contribution', 'test_payout_contribution']


class GrantAdmin(GeneralAdmin):
    """Define the Grant administration layout."""

    ordering = ['-id']
    fields = [
        'migrated_to',
        'title', 'description', 'reference_url', 'admin_address', 'active',
        'amount_received', 'monthly_amount_subscribed',
        'deploy_tx_id', 'cancel_tx_id', 'admin_profile', 'token_symbol',
        'token_address', 'contract_address', 'contract_version', 'network', 'required_gas_price', 'logo_svg_asset',
        'logo_asset', 'created_on', 'modified_on', 'team_member_list',
        'subscriptions_links', 'contributions_links', 'logo', 'logo_svg', 'image_css',
        'link', 'clr_matching', 'clr_prediction_curve', 'hidden', 'grant_type', 'next_clr_calc_date', 'last_clr_calc_date',
        'metadata', 'categories', 'twitter_handle_1', 'twitter_handle_2', 'view_count', 'is_clr_eligible'
    ]
    readonly_fields = [
        'logo_svg_asset', 'logo_asset',
        'team_member_list', 'clr_prediction_curve',
        'subscriptions_links', 'contributions_links', 'link',
        'migrated_to', 'view_count'
    ]
    list_display =['pk', 'title', 'active','grant_type', 'link', 'hidden', 'migrated_to']
    raw_id_fields = ['admin_profile']
    search_fields = ['description', 'admin_profile__handle']


    # Custom Avatars
    def logo_svg_asset(self, instance):
        """Define the logo SVG tag to be displayed in the admin."""
        if instance.logo_svg and instance.logo_svg.url:
            return mark_safe(f'<img src="{instance.svg.url}" width="300" height="300" />')
        return mark_safe('N/A')

    def view_count(self, instance):
        return instance.get_view_count

    def team_member_list(self, instance):
        items = []
        for team_member in instance.team_members.all():
            html = f"<a href={team_member.url}>{team_member.handle}</a>"
            items.append(html)

        return mark_safe(" , ".join(items))

    def link(self, instance):
        try:
            html = f"<a href={instance.url}>{instance.url}</a>"

            return mark_safe(html)
        except:
            return "N/A"

    def logo_asset(self, instance):
        """Define the logo image tag to be displayed in the admin."""
        if instance.logo and instance.logo.url:
            return mark_safe(f'<img src="{instance.logo.url}" width="300" height="300" />')
        return mark_safe('N/A')

    def subscriptions_links(self, instance):
        """Define the logo image tag to be displayed in the admin."""
        eles = []

        for ele in instance.subscriptions.all().order_by('pk'):
            html = f"<a href='{ele.admin_url}'>{ele}</a>"
            eles.append(html)

        return mark_safe("<BR>".join(eles))

    def contributions_links(self, instance):
        """Define the logo image tag to be displayed in the admin."""
        eles = []

        for i in [True, False]:
            html = f"<h3>Success {i}</h3>"
            eles.append(html)
            for ele in instance.contributions.filter(success=i).order_by('-subscription__amount_per_period_usdt'):
                html = f" - <a href='{ele.admin_url}'>{ele}</a>"
                eles.append(html)

        return mark_safe("<BR>".join(eles))

    def migrated_to(self, instance):
        if instance.link_to_new_grant:
            html = f"<a href='{instance.link_to_new_grant.pk}'>{instance.link_to_new_grant.pk}</a>"
            return mark_safe(html)

    logo_svg_asset.short_description = 'Logo SVG Asset'
    logo_asset.short_description = 'Logo Image Asset'



class SubscriptionAdmin(GeneralAdmin):
    """Define the Subscription administration layout."""
    raw_id_fields = ['grant', 'contributor_profile']
    readonly_fields = [
        'contributions_links',
        'error_email_copy_insufficient_balance',
        'error_email_copy_not_active',
    ]

    def contributions_links(self, instance):
        """Define the logo image tag to be displayed in the admin."""
        eles = []

        for sub_ele in instance.subscription_contribution.all():
            html = f"<a href='{sub_ele.admin_url}'>{sub_ele}</a>"
            eles.append(html)

        return mark_safe("<BR>".join(eles))

    def error_email_copy_insufficient_balance(self, instance):
        if not instance.error:
            return ''
        reason = "you dont have enough of a balance of DAI in your account"
        amount = int(instance.amount_per_period)
        html = f"""
<textarea>
hey there,

just wanted to let you know your contribution to https://gitcoin.co/{instance.grant.url} failed because {reason}.  if you want to add {amount} {instance.token_symbol} to {instance.contributor_address} that will make it so we can process the subscription!

let us know.

best,
kevin (team gitcoin)
</textarea>
        """

        return mark_safe(html)

    def error_email_copy_not_active(self, instance):
        if not instance.error:
            return ''
        reason = "you need to top up your balance of DAI in your account"
        amount = float(instance.gas_price / 10 ** 18)
        amount =  str('%.18f' % amount ) + f" {instance.token_symbol} ({amount} {instance.token_symbol})"
        html = f"""
<textarea>
hey there,

just wanted to let you know your contribution to https://gitcoin.co/{instance.grant.url} failed because {reason}.  if you want to add {amount} to {instance.contributor_address} that will make it so we can process the subscription!

let us know.

best,
kevin (team gitcoin)
</textarea>
        """

        return mark_safe(html)



class ContributionAdmin(GeneralAdmin):
    """Define the Contribution administration layout."""
    raw_id_fields = ['subscription']
    list_display = ['id', 'profile', 'created_on', 'grant', 'github_created_on', 'from_ip_address', 'etherscan_links', 'amount', 'token', 'tx_cleared', 'success']
    readonly_fields = ['etherscan_links', 'amount_per_period_to_gitcoin', 'amount_per_period_minus_gas_price', 'amount_per_period']

    def txn_url(self, obj):
        tx_id = obj.tx_id
        if not tx_id:
            tx_id = obj.split_tx_id
        tx_url = 'https://etherscan.io/tx/' + tx_id
        return format_html("<a href='{}' target='_blank'>{}</a>", tx_url, tx_id)

    def profile(self, obj):
        return format_html(f"<a href='/{obj.subscription.contributor_profile.handle}'>{obj.subscription.contributor_profile}</a>")

    def token(self, obj):
        return obj.subscription.token_symbol

    def grant(self, obj):
        return obj.subscription.grant.title

    def amount(self, obj):
        return obj.subscription.amount_per_period

    def github_created_on(self, instance):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(instance.subscription.contributor_profile.github_created_on)

    def from_ip_address(self, instance):
        end = instance.created_on + timezone.timedelta(hours=1)
        start = instance.created_on - timezone.timedelta(hours=1)
        visits = set(instance.subscription.contributor_profile.actions.filter(created_on__gt=start, created_on__lte=end).values_list('ip_address', flat=True))
        visits = [visit for visit in visits if visit]
        return " , ".join(visits)

    def etherscan_links(self, instance):
        html = f"<a href='https://etherscan.io/tx/{instance.tx_id}' target=new>TXID: {instance.tx_id}</a><BR>"
        html += f"<a href='https://etherscan.io/tx/{instance.split_tx_id}' target=new>SPLITTXID: {instance.split_tx_id}</a>"
        return mark_safe(html)

    def amount_per_period(self, instance):
        return instance.subscription.amount_per_period

    def amount_per_period_to_gitcoin(self, instance):
        return instance.subscription.amount_per_period_to_gitcoin

    def amount_per_period_minus_gas_price(self, instance):
        return instance.subscription.amount_per_period_minus_gas_price

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_update_tx_status" in request.POST:
            obj.update_tx_status()
            obj.save()
            self.message_user(request, "tx status pulled from alethio/rpc nodes")
        return redirect(obj.admin_url)


class PhantomFundingAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']
    list_display = ['id', 'github_created_on', 'from_ip_address', '__str__']
    raw_id_fields = ['profile', 'grant']

    def github_created_on(self, instance):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(instance.profile.github_created_on)

    def from_ip_address(self, instance):
        end = instance.created_on + timezone.timedelta(hours=1)
        start = instance.created_on - timezone.timedelta(hours=1)
        visits = set(instance.profile.actions.filter(created_on__gt=start, created_on__lte=end).values_list('ip_address', flat=True))
        visits = [visit for visit in visits if visit]
        return " , ".join(visits)


class CartActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'grant', 'profile', 'action', 'bulk', 'latest', 'created_on']
    raw_id_fields = ['grant', 'profile']
    search_fields = ['bulk', 'action', 'grant']


admin.site.register(PhantomFunding, PhantomFundingAdmin)
admin.site.register(MatchPledge, MatchPledgeAdmin)
admin.site.register(Grant, GrantAdmin)
admin.site.register(Flag, FlagAdmin)
admin.site.register(CLRMatch, CLRMatchAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(CartActivity, CartActivityAdmin)
