# -*- coding: utf-8 -*-
"""Define the Grant admin layout.

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
from django.contrib import admin
from django.utils.safestring import mark_safe

from grants.models import CLRMatch, Contribution, Grant, MatchPledge, Subscription


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


class MatchPledgeAdmin(admin.ModelAdmin):
    """Define the MatchPledge administration layout."""

    ordering = ['-id']
    raw_id_fields = ['profile']


class GrantAdmin(GeneralAdmin):
    """Define the Grant administration layout."""

    ordering = ['-id']
    fields = [
        'title', 'description', 'reference_url', 'admin_address', 'active',
        'amount_goal', 'amount_received', 'monthly_amount_subscribed',
        'deploy_tx_id', 'cancel_tx_id', 'admin_profile', 'token_symbol',
        'token_address', 'contract_address', 'contract_version', 'network', 'required_gas_price', 'logo_svg_asset',
        'logo_asset', 'created_on', 'modified_on', 'team_member_list',
        'subscriptions_links', 'contributions_links', 'logo', 'logo_svg', 'image_css',
         'link', 'clr_matching', 'hidden', 'request_ownership_change'
    ]
    readonly_fields = [
        'logo_svg_asset', 'logo_asset',
        'team_member_list',
        'subscriptions_links', 'contributions_links', 'link', 
    ]
    raw_id_fields = ['admin_profile']

    # Custom Avatars
    def logo_svg_asset(self, instance):
        """Define the logo SVG tag to be displayed in the admin."""
        if instance.logo_svg and instance.logo_svg.url:
            return mark_safe(f'<img src="{instance.svg.url}" width="300" height="300" />')
        return mark_safe('N/A')

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

        for ele in instance.subscriptions.all().order_by('pk'):
            html = f"<a href='{ele.admin_url}'>{ele}</a>"
            eles.append(html)
            for sub_ele in ele.subscription_contribution.all().order_by('pk'):
                html = f" - <a href='{sub_ele.admin_url}'>{sub_ele}</a>"
                eles.append(html)

        return mark_safe("<BR>".join(eles))

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


admin.site.register(MatchPledge, MatchPledgeAdmin)
admin.site.register(Grant, GrantAdmin)
admin.site.register(CLRMatch, GeneralAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contribution, ContributionAdmin)
