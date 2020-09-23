# -*- coding: utf-8 -*-
"""Handle grant URLs.

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
from django.urls import path, re_path

from grants.views import (
    add_grant_from_collection, bulk_fund, bulk_grants_for_cart, clr_grants, flag, get_collection, get_collections_list,
    get_grant_payload, get_grants, get_replaced_tx, grant_activity, grant_categories, grant_details, grant_fund,
    grant_new, grant_new_whitelabel, grants, grants_addr_as_json, grants_bulk_add, grants_by_grant_type,
    grants_cart_view, grants_clr, grants_stats_view, invoice, leaderboard, new_matching_partner, profile, quickstart,
    remove_grant_from_collection, save_collection, subscription_cancel, toggle_grant_favorite, verify_grant,
    zksync_get_interrupt_status, zksync_set_interrupt_status,
)

app_name = 'grants'
urlpatterns = [
    path('', grants, name='grants'),
    path('clr/<slug:round_num>', clr_grants, name='clr_grants'),
    path('clr/<slug:round_num>/', clr_grants, name='clr_grants'),
    path('getstats/', grants_stats_view, name='grants_stats'),
    path('grants.json', grants_addr_as_json, name='grants_json'),
    path('flag/<int:grant_id>', flag, name='grantflag'),
    path('cards_info', get_grants, name='grant_cards_info'),
    path('<int:grant_id>/activity', grant_activity, name='log_activity'),
    path('bulk_cart', bulk_grants_for_cart, name='bulk_grants_for_cart'),
    path('<int:grant_id>/favorite', toggle_grant_favorite, name='favorite_grant'),
    path('activity', grant_activity, name='log_activity'),
    path('<int:grant_id>/<slug:grant_slug>', grant_details, name='details'),
    path('<int:grant_id>/<slug:grant_slug>/', grant_details, name='details2'),
    re_path(r'^matic/new', grant_new_whitelabel, name='new_whitelabel'),
    re_path(r'^new', grant_new, name='new'),
    re_path(r'^categories', grant_categories, name='grant_categories'),
    path('<int:grant_id>/<slug:grant_slug>/fund', grant_fund, name='fund'),
    path('bulk-fund', bulk_fund, name='bulk_fund'),
    path('zksync-set-interrupt-status', zksync_set_interrupt_status, name='zksync_set_interrupt_status'),
    path('zksync-get-interrupt-status', zksync_get_interrupt_status, name='zksync_get_interrupt_status'),
    path('get-replaced-tx', get_replaced_tx, name='get-replaced-tx'),
    path(
        '<int:grant_id>/<slug:grant_slug>/subscription/<int:subscription_id>/cancel',
        subscription_cancel,
        name='subscription_cancel'
    ),
    re_path(r'^profile', profile, name='profile'),
    re_path(r'^quickstart', quickstart, name='quickstart'),
    re_path(r'^leaderboard', leaderboard, name='leaderboard'),
    re_path(r'^matching-partners/new', new_matching_partner, name='new_matching_partner'),
    path(
        'invoice/contribution/<int:contribution_pk>',
        invoice,
        name='contribution_invoice'
    ),
    path('cart/bulk-add/<str:grant_str>', grants_bulk_add, name='grants_bulk_add'),
    path('cart', grants_cart_view, name='cart'),
    path('<slug:grant_type>', grants_by_grant_type, name='grants_by_category2'),
    path('<slug:grant_type>/', grants_by_grant_type, name='grants_by_category'),
    path('v1/api/clr', grants_clr, name='grants_clr'),
    path('v1/api/<int:grant_id>/cart_payload', get_grant_payload, name='grant_payload'),
    path('v1/api/<int:grant_id>/verify', verify_grant, name='verify_grant'),
    path('v1/api/collections/new', save_collection, name='create_collection'),
    path('v1/api/collections/<int:collection_id>', get_collection, name='get_collection'),
    path('v1/api/collections/<int:collection_id>/grants/add', add_grant_from_collection, name='add_grant'),
    path('v1/api/collections/<int:collection_id>/grants/remove', remove_grant_from_collection, name='remove_grant'),
    path('v1/api/collections/', get_collections_list, name='get_collection'),
]
