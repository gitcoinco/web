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
import dashboard.helpers
import dashboard.ios
import dashboard.tip_views
import dashboard.views
import dataviz.d3_views
import enssubdomain.views
import external_bounties.views
import faucet.views
import gitcoinbot.views
import healthcheck.views
import linkshortener.views
import marketing.views
import marketing.webhookviews
import retail.emails
import retail.views
import revenue.views
import tdi.views
from dashboard.router import router as dbrouter
from dataviz.d3_views import viz_graph, viz_scatterplot_stripped
from external_bounties.router import router as ebrouter
from grants.router import router as grant_router
from kudos.router import router as kdrouter
from kudos.views import image as kudos_image
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from .sitemaps import sitemaps

urlpatterns = [
    # JS Internationalization
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # API Views
    url(r'^api/v0.1/profile/(.*)?/keywords', dashboard.views.profile_keywords, name='profile_keywords'),
    url(r'^api/v0.1/funding/save/?', dashboard.ios.save, name='save'),
    url(r'^api/v0.1/faucet/save/?', faucet.views.save_faucet, name='save_faucet'),
    url(r'^api/v0.1/', include(dbrouter.urls)),
    url(r'^api/v0.1/', include(ebrouter.urls)),
    url(r'^api/v0.1/', include(kdrouter.urls)),
    url(r'^api/v0.1/', include(grant_router.urls)),
    url(r'^actions/api/v0.1/', include(dbrouter.urls)),  # same as active
    url(r'^api/v0.1/users_search/', dashboard.views.get_users, name='users_search'),
    url(r'^api/v0.1/kudos_search/', dashboard.views.get_kudos, name='kudos_search'),

    # Health check endpoints
    re_path(r'^health/', include('health_check.urls')),
    re_path(r'^lbcheck/?', healthcheck.views.lbcheck, name='lbcheck'),
    re_path(r'^spec/?', healthcheck.views.spec, name='spec'),

    # Avatar Views
    path('avatar/', include('avatar.urls', namespace='avatar')),

    # Gas Views
    path('gas/', include('gas.urls', namespace='gas')),

    # Grant Views
    path('grants/', include('grants.urls', namespace='grants')),

    # Kudos Views
    path('kudos/', include('kudos.urls', namespace='kudos')),

    # Universe Views
    path('universe/', include('external_bounties.urls', namespace='external_bounties')),

    # Dashboard Views
    # Onboarding Views
    re_path(r'^onboard/(?P<flow>\w+)/$', dashboard.views.onboard, name='onboard'),
    re_path(r'^onboard/contributor/avatar/?$', dashboard.views.onboard_avatar, name='onboard_avatar'),
    url(r'^dashboard/?', dashboard.views.dashboard, name='dashboard'),
    url(r'^explorer/?', dashboard.views.dashboard, name='explorer'),
    path('revenue/attestations/new', revenue.views.new_attestation, name='revenue_new_attestation'),

    # action URLs
    re_path(r'^bounty/quickstart/?', dashboard.views.quickstart, name='quickstart'),
    url(r'^bounty/new/?', dashboard.views.new_bounty, name='new_bounty'),
    re_path(r'^bounty/change/(?P<bounty_id>.*)?', dashboard.views.change_bounty, name='change_bounty'),
    url(r'^funding/new/?', dashboard.views.new_bounty, name='new_funding'),
    url(r'^new/?', dashboard.views.new_bounty, name='new_funding_short'),
    path('issue/fulfill', dashboard.views.fulfill_bounty, name='fulfill_bounty'),
    path('issue/accept', dashboard.views.accept_bounty, name='process_funding'),
    path('issue/advanced_payout', dashboard.views.bulk_payout_bounty, name='bulk_payout_bounty'),
    path('issue/invoice', dashboard.views.invoice, name='invoice'),
    path('issue/payout', dashboard.views.payout_bounty, name='payout_bounty'),
    path('issue/increase', dashboard.views.increase_bounty, name='increase_bounty'),
    path('issue/cancel', dashboard.views.cancel_bounty, name='kill_bounty'),
    path('issue/contribute', dashboard.views.contribute, name='contribute'),
    path('issue/social_contribution', dashboard.views.social_contribution, name='social_contribution'),
    path(
        'actions/bounty/<int:bounty_id>/extend_expiration/',
        dashboard.views.extend_expiration,
        name='extend_expiration'
    ),

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

    # Alpha functionality
    re_path(r'^profile/(.*)?', dashboard.views.profile, name='profile'),
    re_path(r'^toolbox/?', dashboard.views.toolbox, name='toolbox'),
    path('actions/tool/<int:tool_id>/voteUp', dashboard.views.vote_tool_up, name='vote_tool_up'),
    path('actions/tool/<int:tool_id>/voteDown', dashboard.views.vote_tool_down, name='vote_tool_down'),
    re_path(r'^tools/?', dashboard.views.toolbox, name='tools'),

    # images
    re_path(r'^funding/embed/?', dashboard.embed.embed, name='embed'),
    re_path(r'^funding/avatar/?', avatar.views.handle_avatar, name='avatar'),

    # Dynamic
    re_path(r'^dynamic/avatar/(.*)/(.*)?', avatar.views.handle_avatar, name='org_avatar'),
    re_path(r'^dynamic/kudos/(?P<kudos_id>\d+)/(?P<name>\w*)', kudos_image, name='kudos_dynamic_img'),
    re_path(r'^dynamic/viz/graph/(.*)?$', viz_graph, name='viz_graph'),
    re_path(r'^dynamic/viz/sscatterplot/(.*)?$', viz_scatterplot_stripped, name='viz_sscatterplot'),
    path('dynamic/js/tokens_dynamic.js', retail.views.tokens, name='tokens'),

    # sync methods
    url(r'^sync/web3/?', dashboard.views.sync_web3, name='sync_web3'),
    url(r'^sync/get_amount/?', dashboard.helpers.amount, name='helpers_amount'),
    re_path(r'^sync/get_issue_details/?', dashboard.helpers.issue_details, name='helpers_issue_details'),

    # modals
    re_path(r'^modal/get_quickstart_video/?', dashboard.views.get_quickstart_video, name='get_quickstart_video'),
    re_path(r'^modal/extend_issue_deadline/?', dashboard.views.extend_issue_deadline, name='extend_issue_deadline'),

    # brochureware views
    re_path(r'^about/?', retail.views.about, name='about'),
    re_path(r'^mission/?', retail.views.mission, name='mission'),
    re_path(r'^vision/?', retail.views.vision, name='vision'),
    path('not_a_token', retail.views.not_a_token, name='not_a_token'),
    re_path(r'^styleguide-alpha/?', retail.views.ui, name='ui'),
    re_path(r'^results/?(?P<keyword>.*)/?', retail.views.results, name='results_by_keyword'),
    re_path(r'^results/?', retail.views.results, name='results'),
    re_path(r'^activity/?', retail.views.activity, name='activity'),
    re_path(r'^get/?', retail.views.get_gitcoin, name='get_gitcoin'),
    url(r'^$', retail.views.index, name='index'),
    re_path(r'^contributor/?(?P<tech_stack>.*)/?', retail.views.contributor_landing, name='contributor_landing'),
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
    re_path(r'^community/?', retail.views.community, name='community'),
    re_path(r'^slack/?', retail.views.slack, name='slack'),
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
    re_path(r'^settings/(.*)?', marketing.views.email_settings, name='settings'),

    # marketing views
    url(r'^leaderboard/(.*)', marketing.views.leaderboard, name='leaderboard'),
    path('leaderboard', marketing.views._leaderboard, name='_leaderboard'),

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
    re_path(
        r'^legacy/issue/(?P<ghuser>.*)/(?P<ghrepo>.*)/(?P<ghissue>.*)',
        dashboard.views.bounty_details,
        name='legacy_issue_details_new2'
    ),

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

    # wagtail
    re_path(r'^cms/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'', include(wagtail_urls))
]

if settings.ENABLE_SILK:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

if settings.ENV == 'local' and not settings.AWS_STORAGE_BUCKET_NAME:
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
