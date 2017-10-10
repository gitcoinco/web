'''
    Copyright (C) 2017 Gitcoin Core 

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
from django.conf.urls import include, url
from django.contrib import admin
import retail.views
import dashboard.views
import dashboard.helpers
import dashboard.embed
import retail.emails
import tdi.views
import marketing.views

from django.conf.urls import (
    handler400,
    handler403,
    handler404,
    handler500
)
from dashboard.router import router

urlpatterns = [

    # dashboard views
    url(r'^dashboard/?', dashboard.views.dashboard, name='dashboard'),
    url(r'^explorer/?', dashboard.views.dashboard, name='explorer'),
    url(r'^bounty/new/?', dashboard.views.new_bounty, name='new_bounty'),
    url(r'^funding/new/?', dashboard.views.new_bounty, name='new_funding'),
    url(r'^bounty/claim/?', dashboard.views.claim_bounty, name='claim_bounty'),
    url(r'^funding/claim/?', dashboard.views.claim_bounty, name='claim_funding'),
    url(r'^bounty/process/?', dashboard.views.process_bounty, name='process_bounty'),
    url(r'^funding/process/?', dashboard.views.process_bounty, name='process_funding'),
    url(r'^bounty/details/?', dashboard.views.bounty_details, name='bounty_details'),
    url(r'^funding/details/?', dashboard.views.bounty_details, name='funding_details'),
    url(r'^tip/receive/?', dashboard.views.receive_tip, name='receive_tip'),
    url(r'^tip/send/2/?', dashboard.views.send_tip_2, name='send_tip_2'),
    url(r'^tip/send/?', dashboard.views.send_tip, name='send_tip'),
    url(r'^send/?', dashboard.views.send_tip, name='tip'),
    url(r'^tip/?', dashboard.views.send_tip, name='tip'),
    url(r'^legal/?', dashboard.views.terms, name='legal'),
    url(r'^terms/?', dashboard.views.terms, name='_terms'),
    url(r'^legal/terms/?', dashboard.views.terms, name='terms'),
    url(r'^legal/privacy/?', dashboard.views.privacy, name='privacy'),
    url(r'^legal/cookie/?', dashboard.views.cookie, name='cookie'),
    url(r'^legal/prirp/?', dashboard.views.prirp, name='prirp'),
    url(r'^legal/apitos/?', dashboard.views.apitos, name='apitos'),
    url(r'^funding/embed/?', dashboard.embed.embed, name='embed'),
    url(r'^funding/avatar/?', dashboard.embed.avatar, name='avatar'),

    # sync methods
    url(r'^sync/web3', dashboard.views.sync_web3, name='sync_web3'),
    url(r'^sync/get_issue_title?', dashboard.helpers.title, name='helpers_title'),
    url(r'^sync/get_issue_keywords?', dashboard.helpers.keywords, name='helpers_keywords'),
    url(r'^sync/search_save?', dashboard.views.save_search, name='save_search'),

    # brochureware views
    url(r'^about/?', retail.views.about, name='about'),
    url(r'^get/?', retail.views.get_gitcoin, name='get_gitcoin'),
    url(r'^$', retail.views.index, name='index'),
    url(r'^help/dev/?', retail.views.help_dev, name='help_dev'),
    url(r'^help/repo/?', retail.views.help_repo, name='help_repo'),
    url(r'^help/faq?', retail.views.help_faq, name='help_faq'),
    url(r'^help/portal?', retail.views.portal, name='portal'),
    url(r'^help/pilot?', retail.views.help_pilot, name='help_pilot'),
    url(r'^help/?', retail.views.help, name='help'),
    url(r'^extension/?', retail.views.browser_extension, name='browser_extension'),
    url(r'^slack/?', retail.views.slack, name='slack'),
    url(r'^btctalk/?', retail.views.btctalk, name='btctalk'),
    url(r'^reddit/?', retail.views.reddit, name='reddit'),
    url(r'^twitter/?', retail.views.twitter, name='twitter'),
    url(r'^gitter/?', retail.views.gitter, name='gitter'),
    url(r'^fb/?', retail.views.fb, name='fb'),
    url(r'^medium/?', retail.views.medium, name='medium'),
    url(r'^github/?', retail.views.github, name='github'),
    url(r'^youtube/?', retail.views.youtube, name='youtube'),

    #token distribution event
    url(r'^whitepaper/accesscode?', tdi.views.whitepaper_access, name='whitepaper_access'),
    url(r'^whitepaper/?', tdi.views.whitepaper_new, name='whitepaper'),


    # api views
    url(r'^api/v0.1/', include(router.urls)),

    # admin views
    url(r'^_administration/?', admin.site.urls, name='admin'),
    url(r'^_administration/email/new_bounty$', retail.emails.new_bounty, name='new_bounty'),
    url(r'^_administration/email/roundup$', retail.emails.roundup, name='roundup'),
    url(r'^_administration/email/new_tip$', retail.emails.new_tip, name='new_tip'),
    url(r'^_administration/email/new_bounty_claim$', retail.emails.new_bounty_claim, name='new_bounty_claim'),
    url(r'^_administration/email/new_bounty_rejection$', retail.emails.new_bounty_rejection, name='new_bounty_rejection'),
    url(r'^_administration/email/new_bounty_acceptance$', retail.emails.new_bounty_acceptance, name='new_bounty_acceptance'),
    url(r'^_administration/email/bounty_expire_warning$', retail.emails.bounty_expire_warning, name='bounty_expire_warning'),
    url(r'^_administration/process_accesscode_request/(.*)$', tdi.views.process_accesscode_request, name='process_accesscode_request'),
    url(r'^_administration/email/new_tip/resend$', retail.emails.resend_new_tip, name='resend_new_tip'),

    #marketing views
    url(r'^email/settings/(.*)', marketing.views.email_settings, name='email_settings'),
    url(r'^_administration/stats$', marketing.views.stats, name='stats'),


]

handler403 = 'retail.views.handler403'
handler404 = 'retail.views.handler404'
handler500 = 'retail.views.handler500'
handler400 = 'retail.views.handler400'
