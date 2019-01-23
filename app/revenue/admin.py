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

from .models import SKU, ALaCartePurchase, Coupon, Plan, PlanItem, Subscription


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']

admin.site.register(ALaCartePurchase, GeneralAdmin)
admin.site.register(Coupon, GeneralAdmin)
admin.site.register(Plan, GeneralAdmin)
admin.site.register(PlanItem, GeneralAdmin)
admin.site.register(SKU, GeneralAdmin)
admin.site.register(Subscription, GeneralAdmin)
