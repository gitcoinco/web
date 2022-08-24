# -*- coding: utf-8 -*-
"""Define the Grant admin layout.

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
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.messages import constants as messages
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import twitter
from django_svg_image_form_field import SvgAndImageFormField
from grants.models import (
    CartActivity, CLRMatch, Contribution, Flag, Grant, GrantBrandingRoutingPolicy, GrantCLR, GrantCLRCalculation,
    GrantCollection, GrantHallOfFame, GrantHallOfFameGrantee, GrantPayout, GrantStat, GrantTag, GrantType,
    PhantomFunding, Subscription,
)
from grants.views import record_grant_activity_helper
from marketing.mails import grant_more_info_required, new_grant_approved
from web3 import Web3


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


class FlagAdmin(admin.ModelAdmin):
    """Define the FlagAdmin administration layout."""

    ordering = ['-id']
    raw_id_fields = ['profile', 'grant']
    readonly_fields = ['grant_link']

    def grant_link(self, obj):
        return format_html("<a href='/grants/{id}/{slug}' target=\"_blank\">Grant Details</a>", id=obj.grant.id, slug=obj.grant.slug)

    def response_change(self, request, obj):
        if "_post_flag" in request.POST:
            obj.post_flag()
            self.message_user(request, "posted flag to activity feed")
        if "_tweet" in request.POST:
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

class GrantCLRCalculationAdmin(admin.ModelAdmin):
    """Define the GrantCLRCalculation administration layout."""

    ordering = ['-id']
    list_display =['pk', 'latest', 'grant','grantclr','clr_prediction_curve']
    readonly_fields = [
        'grant','grantclr','clr_prediction_curve'
    ]
    search_fields = [
        'grant__title',
        'grantclr__round_num',
        'grantclr__pk'
    ]

class CLRMatchAdmin(admin.ModelAdmin):
    """Define the CLRMatch administration layout."""

    ordering = ['-id']
    list_display =['pk', 'grant', 'round_number', 'amount', 'grant_payout']
    raw_id_fields = ['grant', 'payout_contribution']


class GrantAdmin(GeneralAdmin):
    """Define the Grant administration layout."""

    ordering = ['-id']
    fields = [
        'title', 'is_grant_idle',
        'active', 'visible', 'is_clr_eligible',
        'migrated_to', 'region',
        'grant_type', 'tags_requested', 'tags', 'tag_eligibility_reason',
        'description', 'description_rich', 'github_project_url', 'reference_url',
        'admin_address', 'amount_received', 'amount_received_in_round', 'monthly_amount_subscribed',
        'defer_clr_to', 'deploy_tx_id', 'cancel_tx_id', 'admin_profile', 'token_symbol',
        'token_address', 'contract_address', 'contract_version', 'network', 'required_gas_price', 'logo_svg_asset',
        'logo_asset', 'created_on', 'modified_on', 'team_member_list',
        'subscriptions_links', 'contributions_links', 'logo', 'logo_svg', 'image_css',
        'link', 'clr_prediction_curve', 'hidden', 'next_clr_calc_date', 'last_clr_calc_date',
        'metadata', 'twitter_handle_1', 'twitter_handle_2', 'view_count', 'in_active_clrs',
        'last_update', 'funding_info', 'twitter_verified', 'twitter_verified_by', 'twitter_verified_at', 'stats_history',
        'zcash_payout_address', 'celo_payout_address','zil_payout_address', 'harmony_payout_address', 'binance_payout_address',
        'polkadot_payout_address', 'kusama_payout_address', 'rsk_payout_address', 'algorand_payout_address', 'cosmos_payout_address',
        'emails', 'admin_message', 'has_external_funding'
    ]
    readonly_fields = [
        'defer_clr_to', 'logo_svg_asset', 'logo_asset',
        'team_member_list', 'clr_prediction_curve',
        'subscriptions_links', 'contributions_links', 'link',
        'migrated_to', 'view_count', 'in_active_clrs', 'stats_history',
        'emails', 'is_grant_idle', 'tag_eligibility_reason'
    ]
    list_display =['pk', 'sybil_score', 'weighted_risk_score', 'match_amount', 'positive_round_contributor_count', 'is_clr_eligible', 'title', 'active', 'link', 'hidden', 'migrated_to']
    raw_id_fields = ['admin_profile', 'twitter_verified_by']
    search_fields = ['description', 'admin_profile__handle']

    def is_grant_idle(self, instance):
        return instance.is_idle

    def get_queryset(self, request):
        qs = super(GrantAdmin, self).get_queryset(request)
        self.request = request
        return qs

    # Custom Avatars
    def logo_svg_asset(self, instance):
        """Define the logo SVG tag to be displayed in the admin."""
        if instance.logo_svg and instance.logo_svg.url:
            return mark_safe(f'<img src="{instance.svg.url}" width="300" height="300" />')
        return mark_safe('N/A')

    def emails(self, instance):
        emails = []
        emails.append(instance.admin_profile.email)
        for profile in instance.team_members.all():
            emails.append(profile.email)
        return ",".join(emails)

    def view_count(self, instance):
        return instance.get_view_count

    def match_amount(self, instance):
        try:
            return round(instance.clr_prediction_curve[0][1])
        except:
            return '-'

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
        if not self.request.GET.get('show_data'):
            return mark_safe(f"<a href={instance.admin_url}?show_data=1>Show data</a>")

        """Define the logo image tag to be displayed in the admin."""
        eles = []
        # todo: figure out how to set request
        # if not self.request.GET('expand'):
        #    return mark_safe(f'<a href={instance.admin_url}?expand=t>expand</a>')

        for ele in instance.subscriptions.all().order_by('pk'):
            html = f"<a href='{ele.admin_url}'>{ele}</a>"
            eles.append(html)

        return mark_safe("<BR>".join(eles))

    def response_change(self, request, obj):
        if "_mark_fraud" in request.POST:
            obj.active = False
            obj.is_clr_eligible = False
            obj.visible = False
            obj.save()
            self.message_user(request, "Marked Grant as Fraudulent. Consider blocking the grant admin next?")
        if "_calc_clr" in request.POST:
            from grants.tasks import recalc_clr
            recalc_clr.delay(obj.pk, False)
            self.message_user(request, "recalculation of clr queued")
        if "_request_more_info" in request.POST:
            more_info = request.POST.get('more_info')
            grant_more_info_required(obj, more_info)
            self.message_user(request, "Grant has been successfully approved")
        if "_approve_grant" in request.POST:
            obj.active = True
            obj.is_clr_eligible = True
            obj.hidden = False
            obj.save()
            record_grant_activity_helper('new_grant', obj, obj.admin_profile)
            new_grant_approved(obj, obj.admin_profile)
            self.message_user(request, "Grant has been successfully approved")
        return redirect(obj.admin_url)

    def contributions_links(self, instance):
        if not self.request.GET.get('show_data'):
            return mark_safe(f"<a href={instance.admin_url}?show_data=1>Show data</a>")
        """Define the logo image tag to be displayed in the admin."""
        eles = []

        # todo: figure out how to set request
        #if not self.request.GET('expand'):
        #    return mark_safe(f'<a href={instance.admin_url}?expand=t>expand</a>')

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

    def stats_history(self, instance):
        if not self.request.GET.get('show_data'):
            return mark_safe(f"<a href={instance.admin_url}?show_data=1>Show data</a>")
        html = "<table>"
        html += "<tr><td>Date</td><td>Impressions</td><td>Cart Additions</td><td>Contributions</td></tr>"
        for ele in instance.stats.filter(snapshot_type='increment').order_by('-created_on'):
            html += f'''<tr>
<td>
{ele.created_on.strftime("%m/%d/%Y")}
</td><td>
{ele.data.get('impressions')}
</td><td>
{ele.data.get('in_cart')}
</td><td>
{ele.data.get('contributions')}
</td>
            </tr>'''
        html += "</table>"
        return mark_safe(html)

    logo_svg_asset.short_description = 'Logo SVG Asset'
    logo_asset.short_description = 'Logo Image Asset'

    def save_model(self, request, obj, form, change):
        if obj.admin_address and obj.admin_address not in ["0x0", ""]:
            try:
                obj.admin_address = Web3.toChecksumAddress(obj.admin_address)
                super(GrantAdmin, self).save_model(request, obj, form, change)
            except:
                self.message_user(request, "error: Unable to save due to invalid admin_address. Please enter a valid ETH address", level=messages.ERROR)
        else:
            super(GrantAdmin, self).save_model(request, obj, form, change)


class SubscriptionAdmin(GeneralAdmin):
    """Define the Subscription administration layout."""
    raw_id_fields = ['grant', 'contributor_profile']
    readonly_fields = [
        'contributions_links',
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
    raw_id_fields = ['subscription', 'profile_for_clr']
    list_display = ['pk', 'created_on_nt', 'created_on', 'id', 'user_sybil_score', 'etherscan_links', 'amount_str', 'profile', 'grant', 'tx_cleared', 'success', 'validator_comment']
    readonly_fields = ['etherscan_links', 'amount_per_period_to_gitcoin', 'amount_per_period_minus_gas_price', 'amount_per_period']
    search_fields = ['tx_id', 'split_tx_id', 'subscription__token_symbol']

    def txn_url(self, obj):

        if obj.subscription.tenant == 'ZCASH':
            tx_id = obj.tx_id
            tx_url = 'https://sochain.com/tx/ZEC/' + tx_id

        elif obj.subscription.tenant == 'ETH':
            tx_id = obj.tx_id
            if not tx_id:
                tx_id = obj.split_tx_id
            tx_url = 'https://etherscan.io/tx/' + tx_id

        return format_html("<a href='{}' target='_blank'>{}</a>", tx_url, tx_id)

    def profile(self, obj):
        if obj.subscription.contributor_profile:
            return format_html(f"<a href='/{obj.subscription.contributor_profile.handle}'>{obj.subscription.contributor_profile}</a>")
        return None

    def created_on_nt(self, obj):
        return naturaltime(obj.created_on)

    def amount_str(self, obj):
        return f"{round(obj.subscription.amount_per_period, 2)} {obj.subscription.token_symbol} (${round(obj.subscription.amount_per_period_usdt,2)})"

    def token(self, obj):
        return obj.subscription.token_symbol

    def user_sybil_score(self, obj):
        if obj.subscription.contributor_profile:
            return f"{obj.subscription.contributor_profile.sybil_score} ({obj.subscription.contributor_profile.sybil_score_str})"
        return '0'

    def grant(self, obj):
        return mark_safe(f"<a href={obj.subscription.grant.url}>{obj.subscription.grant.title}</a>")

    def amount(self, obj):
        return obj.subscription.amount_per_period

    def github_created_on(self, instance):
        return naturaltime(instance.subscription.contributor_profile.github_created_on)

    def from_ip_address(self, instance):
        end = instance.created_on + timezone.timedelta(hours=1)
        start = instance.created_on - timezone.timedelta(hours=1)
        visits = set(instance.subscription.contributor_profile.actions.filter(created_on__gt=start, created_on__lte=end).values_list('ip_address', flat=True))
        visits = [visit for visit in visits if visit]
        return " , ".join(visits)

    def etherscan_links(self, instance):
        html = f"<a href='https://etherscan.io/tx/{instance.blockexplorer_url_txid}' target=new>TXID: {instance.tx_id[0:25]}...</a><BR>"
        html += f"<a href='{instance.blockexplorer_url_split_txid}' target=new>SPLITTXID: {instance.split_tx_id[0:25]}...</a>"
        return mark_safe(html)

    def amount_per_period(self, instance):
        return instance.subscription.amount_per_period

    def amount_per_period_to_gitcoin(self, instance):
        return instance.subscription.amount_per_period_to_gitcoin

    def amount_per_period_minus_gas_price(self, instance):
        return instance.subscription.amount_per_period_minus_gas_price

    def response_change(self, request, obj):
        if "_notify_contribution_failure" in request.POST:
            from marketing.mails import grant_txn_failed
            grant_txn_failed(obj)
            obj.validator_comment += f"User Notified {timezone.now()}"
            obj.save()
            self.message_user(request, "notified user of failure")
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


class GrantTypeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    readonly_fields = ['pk']

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        from perftools.management.commands import create_page_cache

        if "_refresh_grants_type_cache" in request.POST:
            create_page_cache.create_grant_type_cache()
            self.message_user(request, f"Grants types cache recreated.")
            return redirect(obj.admin_url)
        elif "_refresh_grant_category_size_cache" in request.POST:
            create_page_cache.create_grant_category_size_cache()
            self.message_user(request, f"Grants category size cache recreated.")
            return redirect(obj.admin_url)
        elif "_refresh_grant_clr_cache" in request.POST:
            create_page_cache.create_grant_clr_cache()
            self.message_user(request, f"Grants clr cache recreated.")
            return redirect(obj.admin_url)

        return super().response_change(request, obj)


class GrantTagAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'is_eligibility_tag']
    readonly_fields = ['pk']

class GrantCLRAdmin(admin.ModelAdmin):
    list_display = ['pk', 'customer_name', 'total_pot', 'round_num', 'sub_round_slug', 'start_date', 'end_date','is_active', 'stats_link']
    raw_id_fields = ['owner']


    def stats_link(self, instance):
        htmls = []
        try:
            url = f'/_administration/mesh?type=grant&year={instance.start_date.strftime("%Y")}&month={instance.start_date.strftime("%m")}&day={instance.start_date.strftime("%d")}&to_year={instance.end_date.strftime("%Y")}&to_month={instance.end_date.strftime("%m")}&to_day={instance.end_date.strftime("%d")}&submit=Go'
            html = f"<a href={url}>mesh</a>"
            htmls.append(html)

            url = f'https://metabase.gitcoin.co/public/question/264bb597-1fab-48ff-90bd-c205e4b43d91?grant_clr={instance.pk}'
            html = f"<a href={url}>leaderboard</a>"
            htmls.append(html)

            url = f'https://metabase.gitcoin.co/dashboard/44?clr_round={instance.round_num}'
            html = f"<a href={url}>stats</a>"
            htmls.append(html)

            return mark_safe(", ".join(htmls))
        except:
            return "N/A"

    def response_change(self, request, obj):
        if "_recalculate_clr" in request.POST:
            from grants.tasks import recalc_clr
            # enqueue this round to be recalculated
            recalc_clr.delay(False, int(obj.pk))
            self.message_user(request, f"submitted recalculation of GrantCLR:{ obj.pk } to queue")

        if "_set_current_grant_clr_calculations_to_false" in request.POST:
            active_calculations = GrantCLRCalculation.objects.filter(grantclr=obj, active=True)

            if active_calculations.count() == 0:
                self.message_user(request, "Active Flag is already false. No action taken")
            else:
                active_calculations.update(active=False)
                self.message_user(request, "Current Grant CLR Calculations's active flag is set to false")

        if "_set_all_grant_clr_calculations_to_false" in request.POST:
            active_calculations = GrantCLRCalculation.objects.filter(active=True)
            if active_calculations.count() == 0:
                self.message_user(request, "Active Flag is already false for all CLRs. No action taken")
            else:
                active_calculations.update(active=False)
                self.message_user(request, "All Grant CLR Calculations's active flag is set to false")

        return redirect(obj.admin_url)


class GrantCollectionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'description', 'hidden', 'cache', 'featured']
    raw_id_fields = ['profile', 'grants', 'curators']
    readonly_fields = ['img']


    def response_change(self, request, obj):
        if "_generate_cache" in request.POST:
            obj.generate_cache()
            self.message_user(request, "generated cache")
        return redirect(obj.admin_url)

    def img(self, instance):
        try:
            html = f'<img src="{instance.cover.url}">'
            return mark_safe(html)
        except:
            return "N/A"


class GrantBrandingRoutingPolicyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'policy_name', 'url_pattern', 'priority' ]

class GrantHallOfFameGranteeInline(admin.StackedInline):
    model = GrantHallOfFameGrantee
    fields = ['grantee', 'name', 'funded_by', 'amount', 'description', 'accomplishment_1', 'accomplishment_2']
    raw_id_fields = ['grantee']
    extra = 1


class GrantHallOfFameForm(forms.ModelForm):
    class Meta:
        model = GrantHallOfFame
        exclude = []
        field_classes = {
            'top_matching_partners': SvgAndImageFormField,
            'top_matching_partners_mobile': SvgAndImageFormField,
            'top_individual_donors': SvgAndImageFormField,
            'top_individual_donors_mobile': SvgAndImageFormField,
        }

class GrantHallOfFameAdmin(admin.ModelAdmin):
    form = GrantHallOfFameForm
    inlines = (GrantHallOfFameGranteeInline, )
    list_display = ['pk', 'total_donations', 'is_published' ]
    readonly_fields = ['is_published', ]

    actions = ['hall_of_fame_publish']

    def hall_of_fame_publish(self, request, queryset):
        object_list = list(queryset)
        if len(object_list) == 1:
            obj = object_list[0]
            obj.publish()
            self.message_user(request, f"The object '{obj}'' successfully marked as published.")
        else:
            self.message_user(request, f"Only 1 object can be published mode. Please select exactly 1 object to set it in published state.", level=messages.WARNING)

    hall_of_fame_publish.short_description = "Publish"


class GrantPayoutAdmin(admin.ModelAdmin):
    """Define the GrantPayout administration layout."""

    list_display =['pk', 'name', 'contract_address']


admin.site.register(PhantomFunding, PhantomFundingAdmin)
admin.site.register(Grant, GrantAdmin)
admin.site.register(Flag, FlagAdmin)
admin.site.register(CLRMatch, CLRMatchAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(CartActivity, CartActivityAdmin)
admin.site.register(GrantType, GrantTypeAdmin)
admin.site.register(GrantTag, GrantTagAdmin)
admin.site.register(GrantCLR, GrantCLRAdmin)
admin.site.register(GrantCollection, GrantCollectionAdmin)
admin.site.register(GrantStat, GeneralAdmin)
admin.site.register(GrantBrandingRoutingPolicy, GrantBrandingRoutingPolicyAdmin)
admin.site.register(GrantCLRCalculation, GrantCLRCalculationAdmin)
admin.site.register(GrantPayout, GrantPayoutAdmin)
admin.site.register(GrantHallOfFame, GrantHallOfFameAdmin)
