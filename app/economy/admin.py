# -*- coding: utf-8 -*-
"""Define Economy related django administration sections.

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
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html

from .models import ConversionRate, Token, TXUpdate


class TokenAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']
    search_fields = ['symbol', 'address']
    list_display = ['id', 'created_on' ,'approved', 'symbol', 'address_url']
    readonly_fields = ['address_url']

    def address_url(self, obj):
        tx_url = 'https://etherscan.io/address/' + obj.address
        return format_html("<a href='{}' target='_blank'>{}</a>", tx_url, obj.address)

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_approve_token" in request.POST:
            from marketing.mails import new_token_request_approved
            new_token_request_approved(obj)
            obj.approved = True
            obj.save()
            self.message_user(request, f"Token approved + requester emailed")
        return redirect(obj.admin_url)


class TXUpdateAdmin(admin.ModelAdmin):
    """Handle displaying conversion rates in the django admin."""

    ordering = ['-id']
    search_fields = ['body']
    list_display = ['id', 'created_on', 'processed', '__str__']


class ConvRateAdmin(admin.ModelAdmin):
    """Handle displaying conversion rates in the django admin."""

    ordering = ['-id']
    search_fields = ['from_currency', 'to_currency']
    list_display =['id', 'timestamp', 'from_currency', 'from_amount','to_currency', 'to_amount', 'source', '__str__']


admin.site.register(ConversionRate, ConvRateAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(TXUpdate, TXUpdateAdmin)
