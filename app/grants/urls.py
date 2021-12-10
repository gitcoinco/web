# -*- coding: utf-8 -*-
"""Handle grant URLs.

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
from django.urls import path, re_path

from grants.views import (
    add_grant_from_collection, api_toggle_user_sybil, bulk_fund, bulk_grants_for_cart, cancel_grant_v1, cart_thumbnail,
    clr_grants, clr_matches, collage, collection_thumbnail, contribute_to_grants_v1, contribution_addr_from_all_as_json,
    contribution_addr_from_grant_as_json, contribution_addr_from_grant_during_round_as_json,
    contribution_addr_from_round_as_json, contribution_info_from_grant_during_round_as_json, create_matching_pledge_v1,
    delete_collection, flag, get_clr_sybil_input, get_collection, get_collections_list, get_ethereum_cart_data,
    get_grant_payload, get_grant_tags, get_grants, get_interrupted_contributions, get_replaced_tx, get_trust_bonus,
    grant_activity, grant_details, grant_details_api, grant_details_contributions, grant_details_contributors,
    grant_edit, grant_fund, grant_new, grants, grants_addr_as_json, grants_bulk_add, grants_by_grant_type,
    grants_cart_view, grants_info, grants_landing, grants_type_redirect, ingest_contributions,
    ingest_contributions_view, invoice, leaderboard, manage_ethereum_cart_data, matching_funds, new_matching_partner,
    profile, quickstart, remove_grant_from_collection, save_collection, toggle_grant_favorite, upload_sybil_csv,
    verify_grant,
)

app_name = 'grants/'
urlpatterns = [
    path('', grants_landing, name='grants'),
    path('explorer', grants, name='grants_explorer'),
    path('explorer/', grants, name='grants_explorer'),
    path('matching_funds', matching_funds, name='matching_funds'),

    # CLR
    path('clr/<int:round_num>', clr_grants, name='clr_grants'),
    path('clr/<int:round_num>/', clr_grants, name='clr_grants'),

    path('clr/<int:round_num>/<str:sub_round_slug>', clr_grants, name='clr_grants'),
    path('clr/<int:round_num>/<str:sub_round_slug>/', clr_grants, name='clr_grants'),

    path('clr/<str:customer_name>/<int:round_num>', clr_grants, name='clr_grants'),
    path('clr/<str:customer_name>/<int:round_num>/', clr_grants, name='clr_grants'),

    path('clr/<str:customer_name>/<int:round_num>/<str:sub_round_slug>', clr_grants, name='clr_grants'),
    path('clr/<str:customer_name>/<int:round_num>/<str:sub_round_slug>/', clr_grants, name='clr_grants'),

    path('grants.json', grants_addr_as_json, name='grants_json'),
    path('flag/<int:grant_id>', flag, name='grantflag'),
    path('cards_info', get_grants, name='grant_cards_info'),
    path('<int:grant_id>/activity', grant_activity, name='log_activity'),
    path('bulk_cart', bulk_grants_for_cart, name='bulk_grants_for_cart'),
    path('<int:grant_id>/favorite', toggle_grant_favorite, name='favorite_grant'),
    path('collage', collage, name='collage'),
    path('activity', grant_activity, name='log_activity'),

    path('cart_thumb/<str:profile>/<str:grants>', cart_thumbnail, name='cart_thumbnail'),
    path('<int:grant_id>/<slug:grant_slug>', grant_details, name='details'),
    path('<int:grant_id>/<slug:grant_slug>/', grant_details, name='details2'),
    path('collections/<int:collection_id>/thumbnail', collection_thumbnail, name='get_collection_thumbnail'),
    re_path(r'^new/?$', grant_new, name='new'),
    path('<int:grant_id>/<slug:grant_slug>/fund', grant_fund, name='fund'),
    path('ingest', ingest_contributions, name='ingest_contributions'),
    path('bulk-fund', bulk_fund, name='bulk_fund'),
    path('manage-ethereum-cart-data', manage_ethereum_cart_data, name='manage_ethereum_cart_data'),
    path('get-ethereum-cart-data', get_ethereum_cart_data, name='get_ethereum_cart_data'),
    path('get-replaced-tx', get_replaced_tx, name='get-replaced-tx'),
    re_path(r'^profile', profile, name='profile'),
    re_path(r'^quickstart', quickstart, name='quickstart'),
    re_path(r'^leaderboard', leaderboard, name='leaderboard'),
    re_path(r'^matching-partners/new', new_matching_partner, name='new_matching_partner'),
    re_path(r'^v1/api/matching-pledge/create', create_matching_pledge_v1, name='create_matching_pledge_v1'),
    path(
        'invoice/contribution/<int:contribution_pk>',
        invoice,
        name='contribution_invoice'
    ),
    path('cart/bulk-add/<str:grant_str>', grants_bulk_add, name='grants_bulk_add'),
    path('cart', grants_cart_view, name='cart'),
    path('add-missing-contributions', ingest_contributions_view, name='ingest_contributions_view'),
    path('get-interrupted-contributions', get_interrupted_contributions, name='get_interrupted_contributions'),
    path('<slug:grant_type>/', grants_type_redirect, name='grants_type_redirect'),
    path('<slug:grant_type>', grants_type_redirect, name='grants_type_redirect2'),
    path('explorer/<slug:grant_type>', grants_by_grant_type, name='grants_by_category2'),
    path('explorer/<slug:grant_type>/', grants_by_grant_type, name='grants_by_category'),
    path('v1/api/tags', get_grant_tags, name='get_grant_tags'),
    path('v1/api/grants', grants_info, name='grants_info'),
    path('v1/api/grant/<int:grant_id>/', grant_details_api, name='grant_details_api'),
    path('v1/api/grant/<int:grant_id>/contributions', grant_details_contributions, name='grant_details_contributions'),
    path('v1/api/grant/<int:grant_id>/contributors', grant_details_contributors, name='grant_details_contributors'),
    path('v1/api/grant/edit/<int:grant_id>/', grant_edit, name='grant_edit'),
    path('v1/api/grant/<int:grant_id>/cancel', cancel_grant_v1, name='cancel_grant_v1'),
    re_path(r'^v1/api/clr-matches/(?P<round_number>\d+)?$', clr_matches, name='clr_matches'),


    path('v1/api/trust-bonus', get_trust_bonus, name='get_trust_bonus'),
    path('v1/api/<int:grant_id>/cart_payload', get_grant_payload, name='grant_payload'),
    path('v1/api/<int:grant_id>/verify', verify_grant, name='verify_grant'),
    path('v1/api/collections/new', save_collection, name='create_collection'),
    path('v1/api/collections/edit', save_collection, name='modify_collection'),
    path('v1/api/collections/delete', delete_collection, name='delete_collection'),
    path('v1/api/collections/<int:collection_id>', get_collection, name='get_collection'),
    path('v1/api/collections/<int:collection_id>/grants/add', add_grant_from_collection, name='add_grant'),
    path('v1/api/collections/<int:collection_id>/grants/remove', remove_grant_from_collection, name='remove_grant'),
    path('v1/api/collections/', get_collections_list, name='get_collection'),
    path('v1/api/contribute', contribute_to_grants_v1, name='contribute_to_grants_v1'),
    path('v1/api/export_addresses/all.json', contribution_addr_from_all_as_json, name='contribution_addr_from_all_as_json'),
    path('v1/api/export_addresses/round<int:round_id>.json', contribution_addr_from_round_as_json, name='contribution_addr_from_round_as_json'),
    path('v1/api/export_addresses/grant<int:grant_id>.json', contribution_addr_from_grant_as_json, name='contribution_addr_from_grant_as_json'),
    path('v1/api/export_addresses/grant<int:grant_id>_round<int:round_id>.json', contribution_addr_from_grant_during_round_as_json, name='contribution_addr_from_grant_during_round_as_json'),
    path('v1/api/export_info/grant<int:grant_id>_round<int:round_id>.json', contribution_info_from_grant_during_round_as_json, name='contribution_addr_from_grant_during_round_as_json'),

    # custom API
    path('v1/api/get-clr-data/<int:round_id>', get_clr_sybil_input, name='get_clr_sybil_input'),
    path('v1/api/toggle_user_sybil', api_toggle_user_sybil, name='api_toggle_user_sybil'),
    path('v1/api/upload_sybil_csv', upload_sybil_csv, name='upload_sybil_csv')

]
