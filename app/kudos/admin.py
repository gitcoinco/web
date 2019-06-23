# -*- coding: utf-8 -*-
"""Define Admin views.

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
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    BulkTransferCoupon, BulkTransferRedemption, Contract, KudosTransfer, Token, TransferEnabledFor, Wallet,
)


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']


class TransferEnabledForAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['token', 'profile']


class BulkTransferCouponAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['sender_profile', 'token']
    readonly_fields = ['claim']

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
    readonly_fields = ['link']

    def link(self, instance):
        html = f"<a href={instance.url}>{instance.url}</a>"
        return mark_safe(html)


class TransferAdmin(admin.ModelAdmin):
    raw_id_fields = ['recipient_profile', 'sender_profile', 'kudos_token', 'kudos_token_cloned_from']
    ordering = ['-id']
    readonly_fields = ['claim']
    search_fields = ['tokenName', 'comments_public', 'from_name', 'username', 'network', 'github_url', 'url', 'emails', 'from_address', 'receive_address', 'txid', 'receive_txid']
    list_display = ['created_on', '__str__']

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
admin.site.register(BulkTransferCoupon, BulkTransferCouponAdmin)
admin.site.register(BulkTransferRedemption, BulkTransferRedemptionAdmin)
admin.site.register(Contract, GeneralAdmin)
