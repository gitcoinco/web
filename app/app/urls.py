'''
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

'''
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

import avatar.views
import bounty_requests.views
import credits.views
import dashboard.embed
import dashboard.gas_views
import dashboard.helpers
import dashboard.tip_views
import dashboard.views
import dataviz.d3_views
import dataviz.views
import faucet.views
import gitcoinbot.views
import healthcheck.views
import kudos.views
import linkshortener.views
import marketing.views
import marketing.webhookviews
import passport.views
import perftools.views
import ptokens.views
import quests.views
import retail.emails
import retail.views
import revenue.views
import search.views
import tdi.views
import townsquare.views
from avatar.router import router as avatar_router
from dashboard.router import router as dbrouter
from grants.router import router as grant_router
from grants.views import cart_thumbnail
from kudos.router import router as kdrouter

from .sitemaps import sitemaps

urlpatterns = [

    # oauth2 provider
    url('^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url('^api/v1/bounty/create', dashboard.views.create_bounty_v1, name='create_bounty_v1'),
    url('^api/v1/bounty/cancel', dashboard.views.cancel_bounty_v1, name='cancel_bounty_v1'),
    url('^api/v1/bounty/fulfill', dashboard.views.fulfill_bounty_v1, name='fulfill_bounty_v1'),
    path('api/v1/bounty/<int:bounty_id>/close', dashboard.views.close_bounty_v1, name='close_bounty_v1'),
    path('api/v1/bounty/payout/<int:fulfillment_id>', dashboard.views.payout_bounty_v1, name='payout_bounty_v1'),
    re_path(r'.*api/v0.1/video/presence$', townsquare.views.video_presence, name='video_presence'),

    # inbox
    re_path(r'^inbox/?', include('inbox.urls', namespace='inbox')),

    # board
    re_path(r'^dashboard/?', dashboard.views.board, name='dashboard'),

    # personal_tokens (now called Time Tokens)
    re_path(r'^ptoken/quickstart/?', ptokens.views.quickstart, name='ptoken_quickstart'),
    re_path(r'^ptoken/faq/?', ptokens.views.faq, name='ptokens_faq'),
    path('ptokens/redemptions/<int:redemption_id>/', ptokens.views.ptoken_redemption, name='token_redemption'),
    path('ptokens/<int:token_id>/purchase/', ptokens.views.ptoken_purchases, name='token_purchase'),
    path('ptokens/<int:token_id>/redemptions/', ptokens.views.ptoken_redemptions, name='token_redemptions'),
    path('ptokens/redemptions/<str:redemption_state>/', ptokens.views.ptoken_redemptions, name='token_redemptions'),
    path('ptokens/me/', ptokens.views.ptoken, name='personal_token'),
    path('ptokens/<int:token_id>/', ptokens.views.ptoken, name='token'),
    path('ptokens/<str:token_state>/', ptokens.views.tokens, name='tokens'),
    path('ptokens/', ptokens.views.tokens, name='tokens'),
    path('ptokens/update', ptokens.views.process_ptokens, name='process_ptokens'),
    path('ptokens/verify', ptokens.views.verification, name='ptoken_verification'),

    # kudos
    re_path(r'^kudos/?$', kudos.views.about, name='kudos_main'),
    re_path(r'^kudos/about/?$', kudos.views.about, name='kudos_about'),
    re_path(r'^kudos/sync/?$', kudos.views.sync, name='kudos_sync'),
    re_path(r'^kudos/marketplace/?$', kudos.views.marketplace, name='kudos_marketplace'),
    re_path(r'^kudos/mint/?$', kudos.views.mint, name='kudos_mint'),
    re_path(r'^kudos/send/?$', kudos.views.send_2, name='kudos_send'),
    path('kudos/send/3/', kudos.views.send_3, name='kudos_send_3'),
    path('kudos/send/4/', kudos.views.send_4, name='kudos_send_4'),
    re_path(r'^lazy_load_kudos/$', dashboard.views.lazy_load_kudos, name='lazy_load_kudos'),
    re_path(r'^kudos/receive/v3/(?P<key>.*)/(?P<txid>.*)/(?P<network>.*)?', kudos.views.receive, name='kudos_receive'),
    re_path(r'^kudos/redeem/(?P<secret>.*)/?$', kudos.views.receive_bulk, name='kudos_receive_bulk'),
    re_path(r'^kudos/search/$', kudos.views.search, name='kudos_search'),
    re_path(
        r'^kudos/(?P<address>\w*)/(?P<token_id>\d+)/(?P<name>\w*)',
        kudos.views.details_by_address_and_token_id,
        name='kudos_details_by_address_and_token_id'
    ),
    re_path(
        r'^kudos/(?P<address>\w*)/(?P<token_id>\d+)',
        kudos.views.details_by_address_and_token_id,
        name='kudos_details_by_address_and_token_id2'
    ),
    re_path(r'^kudos/(?P<kudos_id>\d+)/(?P<name>\w*)', kudos.views.details, name='kudos_details'),
    re_path(r'^kudos/address/(?P<handle>.*)', kudos.views.kudos_preferred_wallet, name='kudos_preferred_wallet'),
    re_path(r'^dynamic/kudos/(?P<kudos_id>\d+)/(?P<name>\w*)', kudos.views.image, name='kudos_dynamic_img'),
    re_path(r'^kudos/new/?', kudos.views.newkudos, name='newkudos'),
    path('dynamic/grants_cart_thumb/<str:profile>/<str:grants>', cart_thumbnail, name='cart_thumbnail'),

    # mailing list
    url('mailing_list/funders/', dashboard.views.funders_mailing_list),
    url('mailing_list/hunters/', dashboard.views.hunters_mailing_list),
    url(r'^api/user/me', dashboard.views.oauth_connect, name='oauth_connect'),
    # api views
    url(r'^api/v0.1/profile/(.*)?/keywords', dashboard.views.profile_keywords, name='profile_keywords'),
    url(r'^api/v0.1/profile/(.*)?/activity.json', dashboard.views.profile_activity, name='profile_activity'),
    url(r'^api/v0.1/profile/(.*)?/earnings.csv', dashboard.views.profile_earnings, name='profile_earnings'),
    url(r'^api/v0.1/profile/(.*)?/grants.csv', dashboard.views.profile_grants, name='profile_grants'),
    url(r'^api/v0.1/profile/(.*)?/quests.csv', dashboard.views.profile_quests, name='profile_quests'),
    url(r'^api/v0.1/profile/(.*)?/ratings/(.*).csv', dashboard.views.profile_ratings, name='profile_ratings'),
    url(r'^api/v0.1/profile/(.*)?/viewers.csv', dashboard.views.profile_viewers, name='profile_viewers'),
    url(r'^api/v0.1/profile/(.*)?/spent.csv', dashboard.views.profile_spent, name='profile_spent'),
    url(r'^api/v0.1/profile/banner', dashboard.views.change_user_profile_banner, name='change_user_profile_banner'),
    url(r'^api/v0.1/profile/settings', dashboard.views.profile_settings, name='profile_settings'),
    url(r'^api/v0.1/profile/backup', dashboard.views.profile_backup, name='profile_backup'),
    path('api/v0.1/activity/<int:activity_id>', townsquare.views.api, name='townsquare_api'),
    path('api/v0.1/comment/<int:comment_id>', townsquare.views.comment_v1, name='comment_v1'),
    path('api/v0.1/emailsettings/', townsquare.views.emailsettings, name='townsquare_emailsettings'),
    url(r'^api/v0.1/activity', retail.views.create_status_update, name='create_status_update'),
    url(
        r'^api/v0.1/profile/(.*)?/jobopportunity',
        dashboard.views.profile_job_opportunity,
        name='profile_job_opportunity'
    ),
    url(
        r'^api/v0.1/profile/(.*)?/setTaxSettings',
        dashboard.views.profile_tax_settings,
        name='profile_set_tax_settings'
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/start_session_idena',
        dashboard.views.start_session_idena,
        name='start_session_idena'
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/authenticate_idena',
        dashboard.views.authenticate_idena,
        name='authenticate_idena'
    ),
    url(r'^api/v0.1/profile/(?P<handle>.*)/logout_idena', dashboard.views.logout_idena, name='logout_idena'),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/brightid_status',
        dashboard.views.recheck_brightid_status,
        name='get_brightid_status'
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/recheck_idena_status',
        dashboard.views.recheck_idena_status,
        name='recheck_idena_status'
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/verify_user_twitter',
        dashboard.views.verify_user_twitter,
        name='verify_user_twitter'
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/verify_user_poap', dashboard.views.verify_user_poap, name='verify_user_poap'
    ),
    url(
        r'^api/v0.1/profile/verify_user_poh', dashboard.views.verify_user_poh, name='verify_user_poh',
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/request_verify_google',
        dashboard.views.request_verify_google,
        name='request_verify_google'
    ),
    url(
        r'^api/v0.1/profile/(?P<handle>.*)/request_verify_facebook',
        dashboard.views.request_verify_facebook,
        name='request_verify_facebook'
    ),
    path('api/v0.1/profile/verify_ens', dashboard.views.verify_profile_with_ens, name='verify_with_ens'),
    url(r'^api/v0.1/profile/verify_user_facebook', dashboard.views.verify_user_facebook, name='verify_user_facebook'),
    url(r'^api/v0.1/profile/verify_user_google', dashboard.views.verify_user_google, name='verify_user_google'),
    # url(
    #     r'^api/v0.1/profile/verify_user_duniter',
    #     dashboard.views.verify_user_duniter,
    #     name='verify_user_duniter'
    # ),
    url(r'^api/v0.1/profile/(?P<handle>.*)', dashboard.views.profile_details, name='profile_details'),
    url(r'^api/v0.1/user_card/(?P<handle>.*)', dashboard.views.user_card, name='user_card'),
    url(r'^api/v0.1/banners', dashboard.views.load_banners, name='load_banners'),
    url(r'^api/v0.1/status_wallpapers', townsquare.views.load_wallpapers, name='load_wallpapers'),
    url(
        r'^api/v0.1/get_suggested_contributors',
        dashboard.views.get_suggested_contributors,
        name='get_suggested_contributors'
    ),
    url(
        r'^api/v0.1/ignore_suggested_tribes/(?P<tribeId>.*)',
        townsquare.views.ignored_suggested_tribe,
        name='ignore_suggested_tribes'
    ),
    url(
        r'^api/v0.1/social_contribution_email',
        dashboard.views.social_contribution_email,
        name='social_contribution_email'
    ),
    url(r'^api/v0.1/org_perms', dashboard.views.org_perms, name='org_perms'),
    url(r'^api/v0.1/bulk_invite', dashboard.views.bulk_invite, name='bulk_invite'),
    url(r'^api/v0.1/faucet/save/?', faucet.views.save_faucet, name='save_faucet'),
    url(r'^api/v0.1/', include(dbrouter.urls)),
    url(r'^api/v0.1/', include(kdrouter.urls)),
    url(r'^api/v0.1/', include(grant_router.urls)),
    url(r'^api/v0.1/', include(avatar_router.urls)),
    url(r'^actions/api/v0.1/', include(dbrouter.urls)),  # same as active
    url(r'^api/v0.1/users_search/', dashboard.views.get_users, name='users_search'),
    url(r'^api/v0.1/kudos_search/', dashboard.views.get_kudos, name='kudos_search'),
    url(r'^api/v0.1/keywords_search/', dashboard.views.get_keywords, name='keywords_search'),
    url(r'^api/v0.1/search/', search.views.get_search, name='search'),
    url(r'^api/v0.1/choose_persona/', dashboard.views.choose_persona, name='choose_persona'),
    url(r'^api/v1/onboard_save/', dashboard.views.onboard_save, name='onboard_save'),
    url(r'^api/v1/file_upload/', dashboard.views.file_upload, name='file_upload'),
    url(r'^api/v1/mautic/(?P<endpoint>.*)', dashboard.views.mautic_api, name='mautic_api'),
    url(r'^api/v1/mautic_profile_save/', dashboard.views.mautic_profile_save, name='mautic_profile_save'),

    # Health check endpoint
    re_path(r'^health/', include('health_check.urls')),
    re_path(r'^lbcheck/?', healthcheck.views.lbcheck, name='lbcheck'),
    re_path(r'^spec/?', healthcheck.views.spec, name='spec'),

    # grant views
    path('grants/', include('grants.urls', namespace='grants')),
    re_path(r'^grants/?', include('grants.urls', namespace='grants_catchall_')),
    re_path(r'^grant/?', include('grants.urls', namespace='grants_catchall')),

    # dashboard views
    re_path(r'^onboard/(?P<flow>\w+)/?$', dashboard.views.onboard, name='onboard'),
    re_path(r'^onboard/contributor/avatar/?$', dashboard.views.onboard_avatar, name='onboard_avatar'),
    re_path(r'^onboard/?$', dashboard.views.onboard, name='onboard'),
    url(r'^postcomment/', dashboard.views.post_comment, name='post_comment'),
    url(r'^explorer/?', dashboard.views.dashboard, name='explorer'),

    # Funder dashboard
    path('funder_dashboard/<str:bounty_type>/', dashboard.views.funder_dashboard, name='funder_dashboard'),
    path(
        'funder_dashboard/bounties/<int:bounty_id>/',
        dashboard.views.funder_dashboard_bounty_info,
        name='funder_dashboard_bounty_info'
    ),
    re_path(r'^sms/request/?$', dashboard.views.send_verification, name='request_verification'),
    re_path(r'^sms/validate/?$', dashboard.views.validate_verification, name='request_verification'),

    # quests
    re_path(r'^quests/?$', quests.views.index, name='quests_index'),
    re_path(r'^quests/next?$', quests.views.next_quest, name='next_quest'),
    re_path(r'^quests/(?P<obj_id>\d+)/feedback', quests.views.feedback, name='quest_feedback'),
    re_path(r'^quests/(?P<obj_id>\d+)/(?P<name>\w*)', quests.views.details, name='quest_details'),
    re_path(r'^quests/new/?', quests.views.editquest, name='newquest'),
    re_path(r'^quests/edit/(?P<pk>\d+)/?', quests.views.editquest, name='editquest'),

    #passport
    re_path(r'^passport/$', passport.views.index, name='passport_gen'),
    path('passport/<str:pattern>', passport.views.passport, name='view_passport'),

    # Contributor dashboard
    path(
        'contributor_dashboard/<str:bounty_type>/', dashboard.views.contributor_dashboard, name='contributor_dashboard'
    ),

    path('revenue/attestations/new', revenue.views.new_attestation, name='revenue_new_attestation'),

    # Hackathons / special events
    path('hackathon/<str:hackathon>/new/', dashboard.views.new_hackathon_bounty, name='new_hackathon_bounty'),
    path('hackathon/<str:hackathon>/new', dashboard.views.new_hackathon_bounty, name='new_hackathon_bounty2'),
    path('hackathon/<str:hackathon>/', dashboard.views.hackathon, name='hackathon'),
    path('hackathon/dashboard/<str:hackathon>', dashboard.views.dashboard_sponsors, name='sponsors-dashboard'),
    path(
        'hackathon/dashboard/<str:hackathon>/<str:panel>',
        dashboard.views.dashboard_sponsors,
        name='sponsors-dashboard'
    ),
    path('hackathon/<str:hackathon>', dashboard.views.hackathon, name='hackathon2'),
    path('hackathon/<str:hackathon>/onboard/', dashboard.views.hackathon_onboard, name='hackathon_onboard2'),
    path('hackathon/<str:hackathon>/<str:panel>/', dashboard.views.hackathon, name='hackathon'),
    path('hackathon/<str:hackathon>/onboard', dashboard.views.hackathon_onboard, name='hackathon_onboard'),
    path('hackathon/onboard/<str:hackathon>', dashboard.views.hackathon_onboard, name='hackathon_onboard2'),
    path('hackathon/onboard/<str:hackathon>/', dashboard.views.hackathon_onboard, name='hackathon_onboard3'),
    path('hackathon/<str:hackathon>/projects/', dashboard.views.hackathon_projects, name='hackathon_projects'),
    path('hackathon/<str:hackathon>/showcase/', dashboard.views.hackathon, name='hackathon_showcase_proxy'),
    path('hackathon/<str:hackathon>/prizes/', dashboard.views.hackathon, name='hackathon_prizes'),
    path('hackathon/<str:hackathon>/townsquare/', dashboard.views.hackathon, name='hackathon_ts'),
    path(
        'hackathon/projects/<str:hackathon>/<str:project>', dashboard.views.hackathon_project, name='hackathon_project'
    ),
    path(
        'hackathon/projects/<str:hackathon>/<str:project>/',
        dashboard.views.hackathon_project,
        name='hackathon_project2'
    ),
    path('modal/new_project/<int:bounty_id>/', dashboard.views.hackathon_get_project, name='hackathon_get_project'),
    path(
        'modal/new_project/<int:bounty_id>/<int:project_id>/',
        dashboard.views.hackathon_get_project,
        name='hackathon_edit_project'
    ),
    path(
        'hackathon/<str:hackathon>/projects/<int:project_id>',
        dashboard.views.hackathon_project_page,
        name='hackathon_project_page'
    ),
    path(
        'hackathon/<str:hackathon>/projects/<int:project_id>/<str:project_name>',
        dashboard.views.hackathon_project_page,
        name='hackathon_project_page'
    ),
    path(
        'hackathon/<str:hackathon>/projects/<int:project_id>/<str:project_name>/<str:tab>/',
        dashboard.views.hackathon_project_page,
        name='hackathon_project_page'
    ),
    path('modal/save_project/', dashboard.views.hackathon_save_project, name='hackathon_save_project'),
    # TODO: revisit if we need to keep these urls for legacy links
    # re_path(r'^hackathon/?$/?', dashboard.views.hackathon, name='hackathon_idx'),
    # re_path(r'^hackathon/(.*)?$', dashboard.views.hackathon, name='hackathon_idx2'),
    url(r'^hackathon/<str:hackathon>/?$/?', dashboard.views.hackathon, name='hackathon'),
    url(r'^hackathon/<str:hackathon>/<str:panel>/?$/?', dashboard.views.hackathon, name='hackathon'),
    path('hackathon-list/', dashboard.views.get_hackathons, name='get_hackathons'),
    path('hackathon-list', dashboard.views.get_hackathons, name='get_hackathons2'),
    re_path(r'^hackathon/?$', dashboard.views.get_hackathons, name='get_hackathons3'),
    re_path(r'^hackathons/?$', dashboard.views.get_hackathons, name='get_hackathons4'),
    url(r'^register_hackathon/', dashboard.views.hackathon_registration, name='hackathon_registration'),
    path('api/v0.1/hackathon/<str:hackathon>/save/', dashboard.views.save_hackathon, name='save_hackathon'),
    path('api/v1/hackathon/<str:hackathon>/prizes', dashboard.views.hackathon_prizes, name='hackathon_prizes_api'),
    path('api/v0.1/hackathon/<str:hackathon>/showcase/', dashboard.views.showcase, name='hackathon_showcase'),
    path('api/v0.1/hackathon/<str:hackathon>/events/', dashboard.views.events, name='hackathon_events'),
    path('api/v0.1/projects/<int:project_id>', dashboard.views.get_project, name='project_context'),
    # action URLs
    url(r'^funder', retail.views.funder_bounties_redirect, name='funder_bounties_redirect'),
    re_path(
        r'^contributor/?(?P<tech_stack>.*)/?',
        retail.views.contributor_bounties_redirect,
        name='contributor_bounties_redirect'
    ),
    url(r'^bounties/funder', retail.views.funder_bounties, name='funder_bounties'),
    re_path(
        r'^bounties/contributor/?(?P<tech_stack>.*)/?', retail.views.contributor_bounties, name='contributor_bounties'
    ),
    re_path(r'^bounty/quickstart/?', dashboard.views.quickstart, name='quickstart'),
    url(r'^bounty/new/?', dashboard.views.new_bounty, name='new_bounty'),
    re_path(r'^bounty/change/(?P<bounty_id>.*)?', dashboard.views.change_bounty, name='change_bounty'),
    url(r'^funding/new/?', dashboard.views.new_bounty, name='new_funding'),  # TODO: Remove
    url(r'^new/?', dashboard.views.new_bounty, name='new_funding_short'),  # TODO: Remove
    # TODO: Rename below to bounty/
    path('issue/fulfill', dashboard.views.fulfill_bounty, name='fulfill_bounty'),
    path('issue/accept', dashboard.views.accept_bounty, name='process_funding'),
    path('issue/advanced_payout', dashboard.views.bulk_payout_bounty, name='bulk_payout_bounty'),
    path('issue/invoice', dashboard.views.invoice, name='invoice'),
    path('issue/payout', dashboard.views.payout_bounty, name='payout_bounty'),
    path('issue/increase', dashboard.views.increase_bounty, name='increase_bounty'),
    path('issue/cancel', dashboard.views.cancel_bounty, name='kill_bounty'),
    path('issue/cancel_reason', dashboard.views.cancel_reason, name='cancel_reason'),
    path('modal/social_contribution', dashboard.views.social_contribution_modal, name='social_contribution_modal'),
    path(
        '<str:bounty_network>/<int:stdbounties_id>/modal/funder_payout_reminder/',
        dashboard.views.funder_payout_reminder_modal,
        name='funder_payout_reminder_modal'
    ),

    # Rating
    path('modal/rating/<int:bounty_id>/<str:username>', dashboard.views.rating_modal, name='rating_modal2'),
    path('modal/rating/<int:bounty_id>/<str:username>/', dashboard.views.rating_modal, name='rating_modal'),
    path('modal/rating_capture/', dashboard.views.rating_capture, name='rating_capture'),
    url(r'^api/v0.1/unrated_bounties/', dashboard.views.unrated_bounties, name='unrated_bounties'),

    # Notify Funder Modal Submission
    path(
        'actions/bounty/<str:bounty_network>/<int:stdbounties_id>/notify/funder_payout_reminder/',
        dashboard.views.funder_payout_reminder,
        name='funder_payout_reminder'
    ),
    path(
        'actions/bounty/<int:bounty_id>/extend_expiration/',
        dashboard.views.extend_expiration,
        name='extend_expiration'
    ),

    # Avatars
    path('avatar/', include('avatar.urls', namespace='avatar')),

    # Interests
    path('actions/bounty/<int:bounty_id>/interest/new/', dashboard.views.new_interest, name='express-interest'),
    path('actions/bounty/<int:bounty_id>/interest/remove/', dashboard.views.remove_interest, name='remove-interest'),
    path(
        'actions/bounty/<int:bounty_id>/interest/<int:profile_id>/uninterested/',
        dashboard.views.uninterested,
        name='uninterested'
    ),

    # View Bounty
    url(
        r'^issue/(?P<ghuser>.*)/(?P<ghrepo>.*)/(?P<ghissue>.*)/(?P<stdbounties_id>.*)',
        dashboard.views.bounty_details,
        name='issue_details_new3'
    ),
    url(
        r'^issue/(?P<ghuser>.*)/(?P<ghrepo>.*)/(?P<ghissue>.*)',
        dashboard.views.bounty_details,
        name='issue_details_new2'
    ),
    re_path(r'^funding/details/?', dashboard.views.bounty_details, name='funding_details'),
    re_path(r'^issue/(?P<invitecode>.*)', dashboard.views.bounty_invite_url, name='unique_bounty_invite'),

    # Tips
    url(
        r'^tip/receive/v3/(?P<key>.*)/(?P<txid>.*)/(?P<network>.*)?',
        dashboard.tip_views.receive_tip_v3,
        name='receive_tip'
    ),
    url(r'^tip/address/(?P<handle>.*)', dashboard.tip_views.tipee_address, name='tipee_address'),
    url(r'^tip/send/4/?', dashboard.tip_views.send_tip_4, name='send_tip_4'),
    url(r'^tip/send/3/?', dashboard.tip_views.send_tip_3, name='send_tip_3'),
    url(r'^tip/send/2/?', dashboard.tip_views.send_tip_2, name='send_tip_2'),
    url(r'^tip/send/?', dashboard.tip_views.send_tip, name='send_tip'),
    url(r'^send/?$', dashboard.tip_views.send_tip, name='tip'),
    url(r'^tip/?$', dashboard.tip_views.send_tip_2, name='tip'),
    url(r'^requestmoney/?', dashboard.tip_views.request_money, name='request_money'),
    # Legal
    re_path(r'^terms/?', dashboard.views.terms, name='_terms'),
    re_path(r'^legal/terms/?', dashboard.views.terms, name='terms'),
    re_path(r'^legal/privacy/?', dashboard.views.privacy, name='privacy'),
    re_path(r'^legal/cookie/?', dashboard.views.cookie, name='cookie'),
    re_path(r'^legal/prirp/?', dashboard.views.prirp, name='prirp'),
    re_path(r'^legal/apitos/?', dashboard.views.apitos, name='apitos'),
    url(r'^legal/?$', dashboard.views.terms, name='legal'),

    # User Directory
    re_path(r'^users/?', dashboard.views.users_directory, name='users_directory'),
    re_path(r'^user_directory/?', dashboard.views.users_directory_elastic, name='users_directory_elastic'),
    re_path(r'^user_lookup/?', dashboard.views.user_lookup, name='user_directory_lookup'),
    re_path(r'^tribes/explore', dashboard.views.users_directory, name='tribes_directory'),

    # Alpha functionality
    re_path(r'^profile/(.*)/(.*)?', dashboard.views.profile, name='profile_by_tab'),
    re_path(r'^profile/(.*)?', dashboard.views.profile, name='profile'),
    re_path(r'^labs/?$', dashboard.views.labs, name='labs'),

    # gas views
    url(r'^gas/faucets/?', dashboard.gas_views.gas_faucet_list, name='gas_faucet_list'),
    url(r'^gas/faq/?', dashboard.gas_views.gas_faq, name='gas_faq'),
    url(r'^gas/intro/?', dashboard.gas_views.gas_intro, name='gas_intro'),
    url(r'^gas/calculator/?', dashboard.gas_views.gas_calculator, name='gas_calculator'),
    url(r'^gas/history/?', dashboard.gas_views.gas_history_view, name='gas_history_view'),
    url(r'^gas/guzzlers/?', dashboard.gas_views.gas_guzzler_view, name='gas_guzzler_view'),
    url(r'^gas/heatmap/?', dashboard.gas_views.gas_heatmap, name='gas_heatmap'),
    url(r'^gas/?$', dashboard.gas_views.gas, name='gas'),

    # images
    re_path(r'^funding/embed/?', dashboard.embed.embed, name='embed'),
    re_path(r'^funding/avatar/?', avatar.views.handle_avatar, name='avatar'),
    re_path(r'^dynamic/avatar/(.*)/(.*)?', avatar.views.handle_avatar, name='org_avatar'),
    re_path(r'^dynamic/avatar/(.*)', avatar.views.handle_avatar, name='org_avatar2'),
    re_path(r'^dynamic/viz/graph/(.*)?$', dataviz.d3_views.viz_graph, name='viz_graph'),
    re_path(r'^dynamic/viz/sscatterplot/(.*)?$', dataviz.d3_views.viz_scatterplot_stripped, name='viz_sscatterplot'),
    path('dynamic/js/tokens_dynamic.js', retail.views.tokens, name='tokens'),
    url('^api/v1/tokens', retail.views.json_tokens, name='json_tokens'),

    # sync methods
    url(r'^sync/web3/?', dashboard.views.sync_web3, name='sync_web3'),
    url(r'^sync/get_amount/?', dashboard.helpers.amount, name='helpers_amount'),
    re_path(r'^sync/get_issue_details/?', dashboard.helpers.issue_details, name='helpers_issue_details'),

    # modals
    re_path(r'^modal/get_quickstart_video/?', dashboard.views.get_quickstart_video, name='get_quickstart_video'),
    re_path(r'^modal/extend_issue_deadline/?', dashboard.views.extend_issue_deadline, name='extend_issue_deadline'),

    # brochureware views
    re_path(r'^homeold/?$', retail.views.index_old, name='homeold'),
    re_path(r'^home/?$', retail.views.index, name='home'),
    re_path(r'^landing/?$', retail.views.index, name='landing'),
    re_path(r'^earn/?$', retail.views.jtbd_earn, name='jtbd_earn'),
    re_path(r'^learn/?$', retail.views.jtbd_learn, name='jtbd_learn'),
    re_path(r'^connect/?$', retail.views.jtbd_connect, name='jtbd_connect'),
    re_path(r'^fund/?$', retail.views.jtbd_fund, name='jtbd_fund'),
    re_path(r'^about/?$', retail.views.about, name='about'),
    re_path(r'^mission/?$', retail.views.mission, name='mission'),
    re_path(r'^jobs/?$', retail.views.jobs, name='jobs'),
    re_path(r'^products/?$', retail.views.products, name='products'),
    re_path(r'^landing/avatar/?', retail.views.avatar, name='avatar_landing'),
    path('not_a_token', retail.views.not_a_token, name='not_a_token'),
    re_path(r'^results/?(?P<keyword>.*)/?', retail.views.results, name='results_by_keyword'),
    re_path(r'^results/?$', retail.views.results, name='results'),
    re_path(r'^activity/?$', retail.views.activity, name='activity'),
    re_path(r'^townsquare/?$', townsquare.views.town_square, name='townsquare'),
    re_path(r'^$', retail.views.index, name='index'),
    re_path(r'^styleguide/components/?', retail.views.styleguide_components, name='styleguide_components'),
    path('action/<int:offer_id>/<slug:offer_slug>/go', townsquare.views.offer_go, name='townsquare_offer_go'),
    path('action/new', townsquare.views.offer_new, name='townsquare_offer_new'),
    path(
        'action/<int:offer_id>/<slug:offer_slug>/decline',
        townsquare.views.offer_decline,
        name='townsquare_offer_decline'
    ),
    path('action/<int:offer_id>/<slug:offer_slug>', townsquare.views.offer_view, name='townsquare_offer_view'),
    url(r'^service/metadata/$', townsquare.views.extract_metadata_page, name='meta-extractor'),
    url(r'^help/dev/?', retail.views.help_dev, name='help_dev'),
    url(r'^help/repo/?', retail.views.help_repo, name='help_repo'),
    url(r'^help/faq/?', retail.views.help_faq, name='help_faq'),
    url(r'^help/portal/?', retail.views.portal, name='portal'),
    url(r'^help/pilot/?', retail.views.help_pilot, name='help_pilot'),
    url(r'^help/?$', retail.views.help, name='help'),
    url(r'^docs/onboard/?', retail.views.onboard, name='onboard_doc'),
    url(r'^extension/chrome/?', retail.views.browser_extension_chrome, name='browser_extension_chrome'),
    url(r'^extension/firefox/?', retail.views.browser_extension_firefox, name='browser_extension_firefox'),
    url(r'^extension/?', retail.views.browser_extension_chrome, name='browser_extension'),
    path('how/<str:work_type>', retail.views.how_it_works, name='how_it_works'),
    re_path(r'^tribes', retail.views.tribes_home, name='tribes'),
    path('tribe/<str:handle>/join/', dashboard.views.join_tribe, name='join_tribe'),
    path('tribe/<str:handle>/save/', dashboard.views.save_tribe, name='save_tribe'),
    path('tribe/title/', dashboard.views.set_tribe_title, name='set_tribe_title'),
    path('tribe/leader/', dashboard.views.tribe_leader, name='tribe_leader'),

    # basic redirect retail views
    re_path(r'^press/?$', retail.views.presskit, name='press'),
    re_path(r'^presskit/?$', retail.views.presskit, name='presskit'),
    re_path(r'^verified/?$', retail.views.verified, name='verified'),
    re_path(r'^community/?$', retail.views.community, name='community'),
    re_path(r'^slack/?$', retail.views.slack, name='slack'),
    re_path(r'^blog/?$', retail.views.blog, name='blog'),
    re_path(r'^submittoken/?$', retail.views.newtoken, name='newtoken'),
    re_path(r'^itunes/?$', retail.views.itunes, name='itunes'),
    re_path(r'^podcast/?$', retail.views.podcast, name='podcast'),
    re_path(r'^casestudy/?$', retail.views.casestudy, name='casestudy'),
    re_path(r'^casestudies/?$', retail.views.casestudy, name='casestudies'),
    re_path(r'^schwag/?$', retail.views.schwag, name='schwag'),
    re_path(r'^btctalk/?$', retail.views.btctalk, name='btctalk'),
    re_path(r'^reddit/?$', retail.views.reddit, name='reddit'),
    re_path(r'^calendar/?$', retail.views.calendar, name='calendar'),
    re_path(r'^livestream/?$', retail.views.calendar, name='livestream'),
    re_path(r'^feedback/?$', retail.views.feedback, name='feedback'),
    re_path(r'^telegram/?$', retail.views.telegram, name='telegram'),
    re_path(r'^twitter/?$', retail.views.twitter, name='twitter'),
    re_path(r'^discord/?$', retail.views.discord, name='discord'),
    re_path(r'^wallpaper/?$', retail.views.wallpaper, name='wallpaper'),
    re_path(r'^wallpapers/?$', retail.views.wallpaper, name='wallpapers'),
    re_path(r'^gitter/?$', retail.views.gitter, name='gitter'),
    re_path(r'^refer/?$', retail.views.refer, name='refer'),
    re_path(r'^fb/?$', retail.views.fb, name='fb'),
    re_path(r'^medium/?$', retail.views.medium, name='medium'),
    re_path(r'^github/?$', retail.views.github, name='github'),
    re_path(r'^youtube/?$', retail.views.youtube, name='youtube'),
    re_path(r'^web3/?$', retail.views.web3, name='web3'),
    re_path(r'^support/?$', retail.views.support, name='support'),


    # increase funding limit
    re_path(r'^requestincrease/?', retail.views.increase_funding_limit_request, name='increase_funding_limit_request'),

    # link shortener
    url(r'^l/(.*)$/?', linkshortener.views.linkredirect, name='redirect'),
    url(r'^credit/(.*)$/?', credits.views.credits, name='credit'),

    # token distribution event
    # re_path(r'^whitepaper/accesscode/?', tdi.views.whitepaper_access, name='whitepaper_access'),
    # re_path(r'^whitepaper/?', tdi.views.whitepaper_new, name='whitepaper'),

    # faucet views
    re_path(r'^faucet/?', faucet.views.faucet, name='faucet'),

    # bounty requests
    re_path(r'^requests/?', bounty_requests.views.bounty_request, name='bounty_requests'),
    url(
        '^api/v1/bounty_request/create',
        bounty_requests.views.create_bounty_request_v1,
        name='create_bounty_request_v1'
    ),
    url(
        '^api/v1/bounty_request/update',
        bounty_requests.views.update_bounty_request_v1,
        name='update_bounty_request_v1'
    ),
    # admin views
    re_path(r'^_administration/?', admin.site.urls, name='admin'),
    path(
        '_administration/email/new_bounty_daily',
        marketing.views.new_bounty_daily_preview,
        name='admin_new_bounty_daily'
    ),
    path('_administration/email/', retail.views.admin_index, name='admin_index_emails'),
    path('_administration/email/grant_cancellation', retail.emails.grant_cancellation, name='admin_grant_cancellation'),
    path(
        '_administration/email/request_amount_email',
        retail.emails.request_amount_email,
        name='admin_request_amount_email'
    ),
    path(
        '_administration/email/featured_funded_bounty',
        retail.emails.featured_funded_bounty,
        name='admin_featured_funded_bounty'
    ),
    path(
        '_administration/email/subscription_terminated',
        retail.emails.subscription_terminated,
        name='admin_subscription_terminated'
    ),
    path('_administration/email/new_grant', retail.emails.new_grant, name='admin_new_grant'),
    path('_administration/email/new_grant_approved', retail.emails.new_grant_approved, name='admin_new_grant_approved'),
    path('_administration/email/new_supporter', retail.emails.new_supporter, name='admin_new_supporter'),
    path(
        '_administration/email/thank_you_for_supporting',
        retail.emails.thank_you_for_supporting,
        name='admin_thank_you_for_supporting'
    ),
    path(
        '_administration/email/support_cancellation',
        retail.emails.support_cancellation,
        name='admin_support_cancellation'
    ),
    path(
        '_administration/email/successful_contribution',
        retail.emails.successful_contribution,
        name='admin_successful_contribution'
    ),
    path(
        '_administration/email/pending_contributions',
        retail.emails.pending_contribution,
        name='admin_pending_contribution'
    ),
    path('_administration/email/new_kudos', retail.emails.new_kudos, name='new_kudos'),
    path('_administration/email/kudos_mint', retail.emails.kudos_mint, name='kudos_mint'),
    path('_administration/email/kudos_mkt', retail.emails.kudos_mkt, name='kudos_mkt'),
    path('_administration/email/new_bounty', retail.emails.new_bounty, name='admin_new_bounty'),
    path('_administration/email/roundup', retail.emails.roundup, name='roundup'),
    path('_administration/email/faucet_rejected', retail.emails.faucet_rejected, name='email_faucet_rejected'),
    path('_administration/email/faucet', retail.emails.faucet, name='email_faucet'),
    path('_administration/email/new_tip', retail.emails.new_tip, name='new_tip'),
    path('_administration/email/new_match', retail.emails.new_match, name='new_match'),
    path('_administration/email/quarterly_roundup', retail.emails.quarterly_roundup, name='quarterly_roundup'),
    path('_administration/email/new_work_submission', retail.emails.new_work_submission, name='new_work_submission'),
    path('_administration/email/weekly_founder_recap', retail.emails.weekly_recap, name='weekly_founder_recap'),
    path(
        '_administration/email/weekly_unread_notifications_email',
        retail.emails.unread_notification_email_weekly_roundup,
        name='unread_notifications_email_weekly_roundup'
    ),
    path('_administration/email/new_bounty_rejection', retail.emails.new_bounty_rejection, name='new_bounty_rejection'),
    path('_administration/email/comment', retail.emails.comment, name='comment_email'),
    path('_administration/email/mention', retail.emails.mention, name='mention_email'),
    path('_administration/email/wallpost', retail.emails.wallpost, name='wallpost_email'),
    path('_administration/email/grant_update', retail.emails.grant_update, name='grant_update_email'),
    path('_administration/email/grant_recontribute', retail.emails.grant_recontribute, name='grant_recontribute_email'),
    path('_administration/email/grant_txn_failed', retail.emails.grant_txn_failed, name='grant_txn_failed_email'),
    path(
        '_administration/email/new_bounty_acceptance',
        retail.emails.new_bounty_acceptance,
        name='new_bounty_acceptance'
    ),
    path(
        '_administration/email/bounty_expire_warning',
        retail.emails.bounty_expire_warning,
        name='bounty_expire_warning'
    ),
    path('_administration/email/bounty_feedback', retail.emails.bounty_feedback, name='bounty_feedback'),
    path('_administration/email/funder_stale', retail.emails.funder_stale, name='funder_stale'),
    path(
        '_administration/email/start_work_expire_warning',
        retail.emails.start_work_expire_warning,
        name='start_work_expire_warning'
    ),
    path('_administration/email/start_work_expired', retail.emails.start_work_expired, name='start_work_expired'),
    path('_administration/email/gdpr_reconsent', retail.emails.gdpr_reconsent, name='gdpr_reconsent'),
    path('_administration/email/share_bounty', retail.emails.share_bounty, name='share_bounty'),
    path('_administration/email/new_tip/resend', retail.emails.resend_new_tip, name='resend_new_tip'),
    path(
        '_administration/email/tribe_hackathon_prizes',
        retail.emails.tribe_hackathon_prizes,
        name='tribe_hackathon_prizes'
    ),
    path(
        '_administration/email/day_email_campaign/<int:day>',
        marketing.views.day_email_campaign,
        name='day_email_campaign'
    ),
    re_path(
        r'^_administration/process_accesscode_request/(.*)$',
        tdi.views.process_accesscode_request,
        name='process_accesscode_request'
    ),
    re_path(
        r'^_administration/process_faucet_request/(.*)$',
        faucet.views.process_faucet_request,
        name='process_faucet_request'
    ),
    re_path(r'^_administration/bulkemail/', dashboard.views.bulkemail, name='bulkemail'),
    re_path(
        r'^_administration/email/start_work_approved$', retail.emails.start_work_approved, name='start_work_approved'
    ),
    re_path(
        r'^_administration/email/start_work_rejected$', retail.emails.start_work_rejected, name='start_work_rejected'
    ),
    re_path(
        r'^_administration/email/start_work_new_applicant$',
        retail.emails.start_work_new_applicant,
        name='start_work_new_applicant'
    ),
    re_path(
        r'^_administration/email/start_work_applicant_about_to_expire$',
        retail.emails.start_work_applicant_about_to_expire,
        name='start_work_applicant_about_to_expire'
    ),
    re_path(
        r'^_administration/email/start_work_applicant_expired$',
        retail.emails.start_work_applicant_expired,
        name='start_work_applicant_expired'
    ),
    re_path(
        r'^_administration/email/funder_payout_reminder$',
        retail.emails.funder_payout_reminder,
        name='funder_payout_reminder'
    ),
    re_path(
        r'^_administration/email/no_applicant_reminder$',
        retail.emails.no_applicant_reminder,
        name='no_applicant_reminder'
    ),
    re_path(r'^_administration/email/match_distribution$', retail.emails.match_distribution, name='match_distribution'),

    # settings
    re_path(r'^settings/email/(.*)', marketing.views.email_settings, name='email_settings'),
    re_path(r'^settings/privacy/?', marketing.views.privacy_settings, name='privacy_settings'),
    re_path(r'^settings/matching/?', marketing.views.matching_settings, name='matching_settings'),
    re_path(r'^settings/feedback/?', marketing.views.feedback_settings, name='feedback_settings'),
    re_path(r'^settings/slack/?', marketing.views.slack_settings, name='slack_settings'),
    re_path(r'^settings/account/?', marketing.views.account_settings, name='account_settings'),
    re_path(r'^settings/tokens/?', marketing.views.token_settings, name='token_settings'),
    re_path(r'^settings/job/?', marketing.views.job_settings, name='job_settings'),
    re_path(r'^settings/organizations/?', marketing.views.org_settings, name='org_settings'),
    re_path(r'^settings/tax/?', marketing.views.tax_settings, name='tax_settings'),
    re_path(r'^settings/(.*)?', marketing.views.email_settings, name='settings'),
    re_path(r'^settings$', marketing.views.org_settings, name='settings2'),

    # marketing views
    url(r'^leaderboard/(.*)', marketing.views.leaderboard, name='leaderboard'),
    path('leaderboard', marketing.views._leaderboard, name='_leaderboard'),

    # dataviz views
    re_path(r'^_administration/stats/$', dataviz.views.stats, name='stats'),
    re_path(r'^_administration/cohort/$', dataviz.views.cohort, name='cohort'),
    re_path(r'^_administration/funnel/$', dataviz.views.funnel, name='funnel'),
    re_path(r'^_administration/viz/?$', dataviz.d3_views.viz_index, name='viz_index'),
    re_path(r'^_administration/mesh/?$', dataviz.d3_views.mesh_network_viz, name='mesh_network_viz'),
    re_path(r'^_administration/viz/sunburst/(.*)?$', dataviz.d3_views.viz_sunburst, name='viz_sunburst'),
    re_path(r'^_administration/viz/chord/(.*)?$', dataviz.d3_views.viz_chord, name='viz_chord'),
    re_path(r'^_administration/viz/steamgraph/(.*)?$', dataviz.d3_views.viz_steamgraph, name='viz_steamgraph'),
    re_path(r'^_administration/viz/circles/(.*)?$', dataviz.d3_views.viz_circles, name='viz_circles'),
    re_path(r'^_administration/viz/sankey/(.*)?$', dataviz.d3_views.viz_sankey, name='viz_sankey'),
    re_path(r'^_administration/viz/spiral/(.*)?$', dataviz.d3_views.viz_spiral, name='viz_spiral'),
    re_path(r'^_administration/viz/heatmap/(.*)?$', dataviz.d3_views.viz_heatmap, name='viz_heatmap'),
    re_path(r'^_administration/viz/calendar/(.*)?$', dataviz.d3_views.viz_calendar, name='viz_calendar'),
    re_path(r'^_administration/viz/draggable/(.*)?$', dataviz.d3_views.viz_draggable, name='viz_draggable'),
    re_path(r'^_administration/viz/scatterplot/(.*)?$', dataviz.d3_views.viz_scatterplot, name='viz_scatterplot'),
    url(r'^blocknative', perftools.views.blocknative, name='blocknative'),

    # quadratic lands
    path('quadraticlands/', include('quadraticlands.urls', namespace='quadraticlands')),
    re_path(r'^quadraticlands/?', include('quadraticlands.urls', namespace='ql_catchall_')),
    re_path(r'^quadraticland/?', include('quadraticlands.urls', namespace='ql_catchall')),

    # for robots
    url(r'^robots.txt/?', retail.views.robotstxt, name='robotstxt'),
    path('sitemap.xml', sitemap_index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path(
        'sitemap-<section>.xml',
        cache_page(86400)(sitemap), {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    # Interests
    path('interest/modal', dashboard.views.get_interest_modal, name='get_interest_modal'),
    path('actions/bounty/<int:bounty_id>/interest/new/', dashboard.views.new_interest, name='express-interest'),
    path('actions/bounty/<int:bounty_id>/interest/remove/', dashboard.views.remove_interest, name='remove-interest'),
    path(
        'actions/bounty/<int:bounty_id>/interest/<int:profile_id>/uninterested/',
        dashboard.views.uninterested,
        name='uninterested'
    ),

    # Legacy Support
    path('legacy/', include('legacy.urls', namespace='legacy')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^gh-login/$', dashboard.views.gh_login, name='gh_login'),
    re_path(r'^login/github$', dashboard.views.gh_login, name='gh_login_'),
    path('', include('social_django.urls', namespace='social')),
    # webhook routes
    # sendgrid webhook processing
    path(settings.SENDGRID_EVENT_HOOK_URL, marketing.webhookviews.process, name='sendgrid_event_process'),

    # gitcoinbot
    url(settings.GITHUB_EVENT_HOOK_URL, gitcoinbot.views.payload, name='payload'),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^api/v0.1/hackathon_project/set_winner/', dashboard.views.set_project_winner, name='project_winner'),
    url(r'^api/v0.1/hackathon_project/set_notes/', dashboard.views.set_project_notes, name='project_notes'),

    # users
    url(r'^api/v0.1/user_bounties/', dashboard.views.get_user_bounties, name='get_user_bounties'),
    url(r'^api/v0.1/users_csv/', dashboard.views.output_users_to_csv, name='users_csv'),
    url(r'^api/v0.1/bounty_mentor/', dashboard.views.bounty_mentor, name='bounty_mentor'),
    url(r'^api/v0.1/users_fetch/', dashboard.views.users_fetch, name='users_fetch'),

]

if settings.ENABLE_SILK:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

urlpatterns += [
    re_path(
        r'^(?!wiki)([a-z|A-Z|0-9|\.](?:[a-z\d]|[A-Z\d]|-(?=[A-Z|a-z\d]))+)/([a-z|A-Z|0-9|\.]+)/?$',
        dashboard.views.profile,
        name='profile_min'
    ),
    re_path(
        r'^(?!wiki)([a-z|A-Z|0-9|\.](?:[a-z\d]|[A-Z\d]|-(?=[A-Z|a-z\d]))+)/?$',
        dashboard.views.profile,
        name='profile_min'
    ),
]

if not settings.AWS_STORAGE_BUCKET_NAME:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# If running in DEBUG, expose the error handling pages.
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^400/$', retail.views.handler400, name='400'),
        re_path(r'^403/$', retail.views.handler403, name='403'),
        re_path(r'^404/$', retail.views.handler404, name='404'),
        re_path(r'^500/$', retail.views.handler500, name='500'),
    ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

LOGIN_REDIRECT_URL = '/login'

handler403 = 'retail.views.handler403'
handler404 = 'retail.views.handler404'
handler500 = 'retail.views.handler500'
handler400 = 'retail.views.handler400'
