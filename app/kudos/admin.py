# -*- coding: utf-8 -*-
"""Define Admin views.

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

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    BulkTransferCoupon, BulkTransferRedemption, Contract, KudosTransfer, Token, TokenRequest, TransferEnabledFor,
    Wallet,
)


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']


class TokenRequestAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['profile__handle', 'name']
    list_display = ['pk', 'profile', 'network', 'created_on', '__str__']
    raw_id_fields = ['profile']
    readonly_fields = ['preview']

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_reject_kudos" in request.POST:
            from marketing.mails import notify_kudos_rejected
            notify_kudos_rejected(obj)
            self.message_user(request, f"Notified user of rejection")
            return redirect('/_administrationkudos/tokenrequest/?approved=f&rejection_reason=')
        if "_change_owner" in request.POST or request.POST.get('_change_owner_mint_kudos', False):
            obj.to_address = '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F'
            obj.save()
            self.message_user(request, f"Changed owner to gitcoin")
        if "_mint_kudos" in request.POST or request.POST.get('_change_owner_mint_kudos', False):
            from kudos.tasks import mint_token_request
            try:
                obj.rejection_reason = 'n/a'
                obj.save()
                mint_token_request(obj.id, num_sync=1)
                self.message_user(request, f"Mint/sync submitted to chain")
            except Exception as e:
                self.message_user(request, str(e))
            return redirect('/_administrationkudos/tokenrequest/?approved=f&rejection_reason=')
        if "_do_sync_kudos" in request.POST:
            from kudos.management.commands.mint_all_kudos import sync_latest
            num_sync = int(request.POST.get('num_sync', 5))
            for i in range(0, num_sync):
                sync_latest(i, network=obj.network)
            self.message_user(request, f"Sync'c Kudos")
            return redirect('/kudos/marketplace')
        return redirect(obj.admin_url)

    def preview(self, instance):
        html = f"<img style='max-width: 400px;' src='{instance.artwork_url}'>"
        return mark_safe(html)


class TransferEnabledForAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['token', 'profile']


class BulkTransferCouponAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['sender_profile', 'token']
    readonly_fields = ['claim']
    search_fields = ['comments_to_put_in_kudos_transfer', 'secret', 'token__name']

    def claim(self, instance):
        url = instance.url
        return format_html(f"<a href={url}>{url}</a>")


class BulkTransferRedemptionAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['coupon', 'redeemed_by', 'kudostransfer']


class TokenAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['name', 'description']
    raw_id_fields = ['contract']
    readonly_fields = ['links', 'view_count']

    def links(self, instance):
        html = f"<a href={instance.url}>{instance.url}</a>"
        other_items = instance.on_networks
        if other_items:
            html += "<BR>also avaialble on :"
        for oi in other_items:
            html += f"<BR> - <a href='{oi[1].url}'>{oi[0]}</a>"
        return mark_safe(html)

    def view_count(self, instance):
        return instance.get_view_count

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "btc_coupon" in request.POST:
            # TODO: mint this token
            import random
            from kudos.views import get_profile
            gitcoinbot = get_profile('gitcoinbot')
            btc = BulkTransferCoupon.objects.create(
                token=obj,
                tag='admin',
                num_uses_remaining=1,
                num_uses_total=1,
                current_uses=0,
                secret=random.randint(10**19, 10**20),
                comments_to_put_in_kudos_transfer=f"Hi from the admin",
                sender_profile=gitcoinbot,
                metadata={
                },
                make_paid_for_first_minutes=0,
                )
            self.message_user(request, f"Created Bulk Transfer Coupon with default settings")
            return redirect(btc.admin_url)
        return redirect(obj.admin_url)


class TransferAdmin(admin.ModelAdmin):
    raw_id_fields = ['recipient_profile', 'sender_profile', 'kudos_token', 'kudos_token_cloned_from']
    ordering = ['-id']
    readonly_fields = ['claim']
    search_fields = ['tokenName', 'comments_public', 'from_name', 'username', 'network', 'github_url', 'url', 'emails', 'from_address', 'receive_address', 'txid', 'receive_txid']
    list_display = ['created_on', '__str__']

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_broadcast_txn" in request.POST:
            from kudos.tasks import redeem_bulk_kudos
            redeem_bulk_kudos.delay(obj.pk, send_notif_email=True)
            self.message_user(request, f"submitted broadcast to queues")
            return redirect(obj.admin_url)

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


admin.site.register(TransferEnabledFor, TransferEnabledForAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(KudosTransfer, TransferAdmin)
admin.site.register(Wallet, GeneralAdmin)
admin.site.register(TokenRequest, TokenRequestAdmin)
admin.site.register(BulkTransferCoupon, BulkTransferCouponAdmin)
admin.site.register(BulkTransferRedemption, BulkTransferRedemptionAdmin)
admin.site.register(Contract, GeneralAdmin)
