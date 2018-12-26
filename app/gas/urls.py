# -*- coding: utf-8 -*-
"""Handle gas URLs.

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
from django.urls import re_path

from .views import (
    gas, gas_calculator, gas_faq, gas_faucet_list, gas_guzzler_view, gas_heatmap, gas_history_view, gas_intro,
)

app_name = 'gas'
urlpatterns = [
    re_path(r'^', gas, name='index'),
    re_path(r'^calculator/?', gas_calculator, name='calculator'),
    re_path(r'^faq/?', gas_faq, name='faq'),
    re_path(r'^faucets/?', gas_faucet_list, name='faucet_list'),
    re_path(r'^guzzlers/?', gas_guzzler_view, name='guzzler_view'),
    re_path(r'^heatmap/?', gas_heatmap, name='heatmap'),
    re_path(r'^history/?', gas_history_view, name='history_view'),
    re_path(r'^intro/?', gas_intro, name='intro'),
]
