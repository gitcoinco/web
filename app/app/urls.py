'''
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

'''
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
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
import enssubdomain.views
# event:ethdenver2019
import event_ethdenver2019.views
import faucet.views
import gitcoinbot.views
import healthcheck.views
import kudos.views
import linkshortener.views
import marketing.views
import marketing.webhookviews
import retail.emails
import retail.views
import revenue.views
import tdi.views
from avatar.router import router as avatar_router
from dashboard.router import router as dbrouter
from grants.router import router as grant_router
from kudos.router import router as kdrouter

from .sitemaps import sitemaps

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # create bounty
    url(r'^create?', dashboard.views.new_bounty, name='create_bounty'),  # TODO: Remove

    # inbox
    path('inbox/', include('inbox.urls', namespace='inbox')),

    # board
    path('dashboard/', dashboard.views.board, name='dashboard'),

    # kudos
    path('kudos/', kudos.views.about, name='kudos_main'),
    path('kudos/about/', kudos.views.about, name='kudos_about'),
    path('kudos/marketplace/', kudos.views.marketplace, name='kudos_marketplace'),
    path('kudos/mint/', kudos.views.mint, name='kudos_mint'),
    path('kudos/send/', kudos.views.send_2, name='kudos_send'),
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
    re_path(r'^kudos/(?P<kudos_id>\d+)/(?P<name>\w*)', kudos.views.details, name='kudos_details'),
    re_path(r'^kudos/address/(?P<handle>.*)', kudos.views.kudos_preferred_wallet, name='kudos_preferred_wallet'),
    re_path(r'^dynamic/kudos/(?P<kudos_id>\d+)/(?P<name>\w*)', kudos.views.image, name='kudos_dynamic_img'),

    # mailing list
    url('mailing_list/funders/', dashboard.views.funders_mailing_list),
    url('mailing_list/hunters/', dashboard.views.hunters_mailing_list),

    # api views
    url(r'^api/v0.1/profile/(.*)?/keywords', dashboard.views.profile_keywords, name='profile_keywords'),
    url(r'^api/v0.1/profile/banner', dashboard.views.change_user_profile_banner, name='change_user_profile_banner'),
    url(
        r'^api/v0.1/profile/(.*)?/jobopportunity',
        dashboard.views.profile_job_opportunity,
        name='profile_job_opportunity'
    ),
    url(r'^api/v0.1/profile/(?P<handle>.*)', dashboard.views.profile_details, name='profile_details'),
    url(r'^api/v0.1/banners', dashboard.views.load_banners, name='load_banners'),
    url(
        r'^api/v0.1/get_suggested_contributors',
        dashboard.views.get_suggested_contributors,
        name='get_suggested_contributors'
    ),
    url(
        r'^api/v0.1/social_contribution_email',
        dashboard.views.social_contribution_email,
        name='social_contribution_email'
    ),
    url(r'^api/v0.1/bountydocument', dashboard.views.bounty_upload_nda, name='bounty_upload_nda'),
    url(r'^api/v0.1/faucet/save/?', faucet.views.save_faucet, name='save_faucet'),
    url(r'^api/v0.1/', include(dbrouter.urls)),
    url(r'^api/v0.1/', include(kdrouter.urls)),
    url(r'^api/v0.1/', include(grant_router.urls)),
    url(r'^api/v0.1/', include(avatar_router.urls)),
    url(r'^actions/api/v0.1/', include(dbrouter.urls)),  # same as active
    url(r'^api/v0.1/users_search/', dashboard.views.get_users, name='users_search'),
    url(r'^api/v0.1/kudos_search/', dashboard.views.get_kudos, name='kudos_search'),
    url(r'^api/v0.1/choose_persona/', dashboard.views.choose_persona, name='choose_persona'),

    # Health check endpoint
    re_path(r'^health/', include('health_check.urls')),
    re_path(r'^lbcheck/?', healthcheck.views.lbcheck, name='lbcheck'),
    re_path(r'^spec/?', healthcheck.views.spec, name='spec'),

    # grant views
    path('grants/', include('grants.urls', namespace='grants')),

    # dashboard views
    re_path(r'^onboard/(?P<flow>\w+)/$', dashboard.views.onboard, name='onboard'),
    re_path(r'^onboard/contributor/avatar/?$', dashboard.views.onboard_avatar, name='onboard_avatar'),
    url(r'^postcomment/', dashboard.views.post_comment, name='post_comment'),
    url(r'^explorer/?', dashboard.views.dashboard, name='explorer'),

    # Funder dashboard
    path('funder_dashboard/<str:bounty_type>/', dashboard.views.funder_dashboard, name='funder_dashboard'),
    path('funder_dashboard/bounties/<int:bounty_id>/', dashboard.views.funder_dashboard_bounty_info, name='funder_dashboard_bounty_info'),

    # Contributor dashboard
    path('contributor_dashboard/<str:bounty_type>/', dashboard.views.contributor_dashboard, name='contributor_dashboard'),

    # Hackathon static page
    url(r'^hackathon/ethhack2019', dashboard.views.ethhack, name='ethhack_2019'),
    url(r'^hackathon/beyondblocks', dashboard.views.beyond_blocks_2019, name='beyond_blocks_2019'),
    path('revenue/attestations/new', revenue.views.new_attestation, name='revenue_new_attestation'),

    # Hackathons / special events
    re_path(r'^hackathon/(?P<hackathon>.*)?/', dashboard.views.hackathon, name='hackathon'),
    re_path(r'^hackathon?/', dashboard.views.hackathon, name='hackathon_idx'),
    path('hackathon-list/', dashboard.views.get_hackathons, name='get_hackathons'),

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
    path('issue/refund_request', dashboard.views.refund_request, name='refund_request'),
    path('issue/cancel_reason', dashboard.views.cancel_reason, name='cancel_reason'),
    path('issue/contribute', dashboard.views.contribute, name='contribute'),
    path('issue/social_contribution', dashboard.views.social_contribution, name='social_contribution'),
    path('modal/social_contribution', dashboard.views.social_contribution_modal, name='social_contribution_modal'),
    path(
        '<str:bounty_network>/<int:stdbounties_id>/modal/funder_payout_reminder/',
        dashboard.views.funder_payout_reminder_modal,
        name='funder_payout_reminder_modal'
    ),

    # Rating
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
    url(r'^send/?', dashboard.tip_views.send_tip, name='tip'),
    url(r'^tip/?', dashboard.tip_views.send_tip, name='tip'),

    # Legal
    re_path(r'^terms/?', dashboard.views.terms, name='_terms'),
    re_path(r'^legal/terms/?', dashboard.views.terms, name='terms'),
    re_path(r'^legal/privacy/?', dashboard.views.privacy, name='privacy'),
    re_path(r'^legal/cookie/?', dashboard.views.cookie, name='cookie'),
    re_path(r'^legal/prirp/?', dashboard.views.prirp, name='prirp'),
    re_path(r'^legal/apitos/?', dashboard.views.apitos, name='apitos'),
    re_path(r'^legal/?', dashboard.views.terms, name='legal'),
    re_path(r'^users/?', dashboard.views.users_directory, name='users_directory'),

    # Alpha functionality
    re_path(r'^profile/(.*)?', dashboard.views.profile, name='profile'),
    re_path(r'^toolbox/?', dashboard.views.toolbox, name='toolbox'),
    path('actions/tool/<int:tool_id>/voteUp', dashboard.views.vote_tool_up, name='vote_tool_up'),
    path('actions/tool/<int:tool_id>/voteDown', dashboard.views.vote_tool_down, name='vote_tool_down'),
    re_path(r'^tools/?', dashboard.views.toolbox, name='tools'),
    re_path(r'^labs/?', dashboard.views.labs, name='labs'),

    # gas views
    url(r'^gas/faucets/?', dashboard.gas_views.gas_faucet_list, name='gas_faucet_list'),
    url(r'^gas/faq/?', dashboard.gas_views.gas_faq, name='gas_faq'),
    url(r'^gas/intro/?', dashboard.gas_views.gas_intro, name='gas_intro'),
    url(r'^gas/calculator/?', dashboard.gas_views.gas_calculator, name='gas_calculator'),
    url(r'^gas/history/?', dashboard.gas_views.gas_history_view, name='gas_history_view'),
    url(r'^gas/guzzlers/?', dashboard.gas_views.gas_guzzler_view, name='gas_guzzler_view'),
    url(r'^gas/heatmap/?', dashboard.gas_views.gas_heatmap, name='gas_heatmap'),
    url(r'^gas/?', dashboard.gas_views.gas, name='gas'),

    # images
    re_path(r'^funding/embed/?', dashboard.embed.embed, name='embed'),
    re_path(r'^funding/avatar/?', avatar.views.handle_avatar, name='avatar'),
    re_path(r'^dynamic/avatar/(.*)/(.*)?', avatar.views.handle_avatar, name='org_avatar'),
    re_path(r'^dynamic/viz/graph/(.*)?$', dataviz.d3_views.viz_graph, name='viz_graph'),
    re_path(r'^dynamic/viz/sscatterplot/(.*)?$', dataviz.d3_views.viz_scatterplot_stripped, name='viz_sscatterplot'),
    path('dynamic/js/tokens_dynamic.js', retail.views.tokens, name='tokens'),

    # sync methods
    url(r'^sync/web3/?', dashboard.views.sync_web3, name='sync_web3'),
    url(r'^sync/get_amount/?', dashboard.helpers.amount, name='helpers_amount'),
    re_path(r'^sync/get_issue_details/?', dashboard.helpers.issue_details, name='helpers_issue_details'),

    # modals
    re_path(r'^modal/get_quickstart_video/?', dashboard.views.get_quickstart_video, name='get_quickstart_video'),
    re_path(r'^modal/extend_issue_deadline/?', dashboard.views.extend_issue_deadline, name='extend_issue_deadline'),

    # brochureware views
    re_path(r'^$', retail.views.index, name='index'),
    re_path(r'^pricing/$', retail.views.pricing, name='pricing'),
    re_path(r'^subscribe/$', retail.views.subscribe, name='subscribe'),
    re_path(r'^about/?', retail.views.about, name='about'),
    re_path(r'^mission/?', retail.views.mission, name='mission'),
    re_path(r'^jobs/?', retail.views.jobs, name='jobs'),
    re_path(r'^vision/?', retail.views.vision, name='vision'),
    re_path(r'^products/?', retail.views.products, name='products'),
    path('not_a_token', retail.views.not_a_token, name='not_a_token'),
    re_path(r'^results/?(?P<keyword>.*)/?', retail.views.results, name='results_by_keyword'),
    re_path(r'^results/?', retail.views.results, name='results'),
    re_path(r'^activity/?', retail.views.activity, name='activity'),
    url(r'^help/dev/?', retail.views.help_dev, name='help_dev'),
    url(r'^help/repo/?', retail.views.help_repo, name='help_repo'),
    url(r'^help/faq/?', retail.views.help_faq, name='help_faq'),
    url(r'^help/portal/?', retail.views.portal, name='portal'),
    url(r'^help/pilot/?', retail.views.help_pilot, name='help_pilot'),
    url(r'^help/?', retail.views.help, name='help'),
    url(r'^docs/onboard/?', retail.views.onboard, name='onboard_doc'),
    url(r'^extension/chrome/?', retail.views.browser_extension_chrome, name='browser_extension_chrome'),
    url(r'^extension/firefox/?', retail.views.browser_extension_firefox, name='browser_extension_firefox'),
    url(r'^extension/?', retail.views.browser_extension_chrome, name='browser_extension'),
    path('how/<str:work_type>', retail.views.how_it_works, name='how_it_works'),

    # basic redirect retail views
    re_path(r'^press/?', retail.views.presskit, name='press'),
    re_path(r'^presskit/?', retail.views.presskit, name='presskit'),
    re_path(r'^verified/?', retail.views.verified, name='verified'),
    re_path(r'^community/?', retail.views.community, name='community'),
    re_path(r'^slack/?', retail.views.slack, name='slack'),
    re_path(r'^blog/?', retail.views.blog, name='blog'),
    re_path(r'^submittoken/?', retail.views.newtoken, name='newtoken'),
    re_path(r'^itunes/?', retail.views.itunes, name='itunes'),
    re_path(r'^podcast/?', retail.views.podcast, name='podcast'),
    re_path(r'^casestudy/?', retail.views.casestudy, name='casestudy'),
    re_path(r'^casestudies/?', retail.views.casestudy, name='casestudies'),
    re_path(r'^schwag/?', retail.views.schwag, name='schwag'),
    re_path(r'^btctalk/?', retail.views.btctalk, name='btctalk'),
    re_path(r'^reddit/?', retail.views.reddit, name='reddit'),
    re_path(r'^livestream/?', retail.views.livestream, name='livestream'),
    re_path(r'^feedback/?', retail.views.feedback, name='feedback'),
    re_path(r'^twitter/?', retail.views.twitter, name='twitter'),
    re_path(r'^gitter/?', retail.views.gitter, name='gitter'),
    re_path(r'^refer/?', retail.views.refer, name='refer'),
    re_path(r'^fb/?', retail.views.fb, name='fb'),
    re_path(r'^medium/?', retail.views.medium, name='medium'),
    re_path(r'^github/?', retail.views.github, name='github'),
    re_path(r'^youtube/?', retail.views.youtube, name='youtube'),
    re_path(r'^web3/?', retail.views.web3, name='web3'),

    # increase funding limit
    re_path(r'^requestincrease/?', retail.views.increase_funding_limit_request, name='increase_funding_limit_request'),

    # link shortener
    url(r'^l/(.*)$/?', linkshortener.views.linkredirect, name='redirect'),
    url(r'^credit/(.*)$/?', credits.views.credits, name='credit'),

    # token distribution event
    re_path(r'^whitepaper/accesscode/?', tdi.views.whitepaper_access, name='whitepaper_access'),
    re_path(r'^whitepaper/?', tdi.views.whitepaper_new, name='whitepaper'),

    # faucet views
    re_path(r'^faucet/?', faucet.views.faucet, name='faucet'),

    # bounty requests
    re_path(r'^requests/?', bounty_requests.views.bounty_request, name='bounty_requests'),

    # admin views
    re_path(r'^_administration/?', admin.site.urls, name='admin'),
    path('_administration/email/grant_cancellation', retail.emails.grant_cancellation, name='admin_grant_cancellation'),
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
    path(
        '_administration/email/change_grant_owner_request',
        retail.emails.change_grant_owner_request,
        name='admin_change_grant_owner_request'
    ),
    path(
        '_administration/email/change_grant_owner_accept',
        retail.emails.change_grant_owner_accept,
        name='admin_change_grant_owner_accept'
    ),
    path(
        '_administration/email/notify_ownership_change',
        retail.emails.notify_ownership_change,
        name='admin_notify_ownership_change'
    ),
    path(
        '_administration/email/change_grant_owner_reject',
        retail.emails.change_grant_owner_reject,
        name='admin_change_grant_owner_reject'
    ),
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
    re_path(
        r'^_administration/process_refund_request/(.*)$',
        dashboard.views.process_refund_request,
        name='process_refund_request'
    ),
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

    # settings
    re_path(r'^settings/email/(.*)', marketing.views.email_settings, name='email_settings'),
    re_path(r'^settings/privacy/?', marketing.views.privacy_settings, name='privacy_settings'),
    re_path(r'^settings/matching/?', marketing.views.matching_settings, name='matching_settings'),
    re_path(r'^settings/feedback/?', marketing.views.feedback_settings, name='feedback_settings'),
    re_path(r'^settings/slack/?', marketing.views.slack_settings, name='slack_settings'),
    re_path(r'^settings/discord/?', marketing.views.discord_settings, name='discord_settings'),
    re_path(r'^settings/ens/?', marketing.views.ens_settings, name='ens_settings'),
    re_path(r'^settings/account/?', marketing.views.account_settings, name='account_settings'),
    re_path(r'^settings/tokens/?', marketing.views.token_settings, name='token_settings'),
    re_path(r'^settings/job/?', marketing.views.job_settings, name='job_settings'),
    re_path(r'^settings/(.*)?', marketing.views.email_settings, name='settings'),

    # marketing views
    url(r'^leaderboard/(.*)', marketing.views.leaderboard, name='leaderboard'),
    path('leaderboard', marketing.views._leaderboard, name='_leaderboard'),

    # dataviz views
    re_path(r'^_administration/stats/$', dataviz.views.stats, name='stats'),
    re_path(r'^_administration/cohort/$', dataviz.views.cohort, name='cohort'),
    re_path(r'^_administration/funnel/$', dataviz.views.funnel, name='funnel'),
    re_path(r'^_administration/viz/?$', dataviz.d3_views.viz_index, name='viz_index'),
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

    # for robots
    url(r'^robots.txt/?', retail.views.robotstxt, name='robotstxt'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
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
    path('', include('social_django.urls', namespace='social')),
    # webhook routes
    # sendgrid webhook processing
    path(settings.SENDGRID_EVENT_HOOK_URL, marketing.webhookviews.process, name='sendgrid_event_process'),

    # ENS urls
    re_path(r'^ens/', enssubdomain.views.ens_subdomain, name='ens'),

    # gitcoinbot
    url(settings.GITHUB_EVENT_HOOK_URL, gitcoinbot.views.payload, name='payload'),
    url(r'^impersonate/', include('impersonate.urls')),

    # event:ethdenver2019
    re_path(
        r'^ethdenver/redeem/(?P<secret>.*)/?$',
        event_ethdenver2019.views.receive_bulk_ethdenver,
        name='kudos_receive_bulk'
    ),
    url(r'^ethdenver/', event_ethdenver2019.views.ethdenver2019),
    # /event:ethdenver2019

    # users
    url(r'^api/v0.1/user_bounties/', dashboard.views.get_user_bounties, name='get_user_bounties'),
    url(r'^api/v0.1/users_fetch/', dashboard.views.users_fetch, name='users_fetch'),
]

if settings.ENABLE_SILK:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

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

handler403 = 'retail.views.handler403'
handler404 = 'retail.views.handler404'
handler500 = 'retail.views.handler500'
handler400 = 'retail.views.handler400'
