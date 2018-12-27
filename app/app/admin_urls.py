# -*- coding: utf-8 -*-
"""Handle admin specific URLs.

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
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path

from dataviz import d3_views as dataviz_d3_views
from dataviz import views as dataviz_views
from faucet.views import process_faucet_request
from retail import emails as retail_emails
from tdi.views import process_accesscode_request

app_name = '_administration'
urlpatterns = [
    # Email Previews
    path('email/grant_cancellation', retail_emails.grant_cancellation, name='admin_grant_cancellation'),
    path('email/subscription_terminated', retail_emails.subscription_terminated, name='admin_subscription_terminated'),
    path('email/new_grant', retail_emails.new_grant, name='admin_new_grant'),
    path('email/new_supporter', retail_emails.new_supporter, name='admin_new_supporter'),
    path(
        'email/thank_you_for_supporting', retail_emails.thank_you_for_supporting, name='admin_thank_you_for_supporting'
    ),
    path('email/support_cancellation', retail_emails.support_cancellation, name='admin_support_cancellation'),
    path('email/successful_contribution', retail_emails.successful_contribution, name='admin_successful_contribution'),
    path('email/new_kudos', retail_emails.new_kudos, name='new_kudos'),
    path('email/kudos_mint', retail_emails.kudos_mint, name='kudos_mint'),
    path('email/kudos_mkt', retail_emails.kudos_mkt, name='kudos_mkt'),
    path('email/new_bounty', retail_emails.new_bounty, name='admin_new_bounty'),
    path('email/roundup', retail_emails.roundup, name='roundup'),
    path('email/faucet_rejected', retail_emails.faucet_rejected, name='email_faucet_rejected'),
    path('email/faucet', retail_emails.faucet, name='email_faucet'),
    path('email/new_tip', retail_emails.new_tip, name='new_tip'),
    path('email/new_match', retail_emails.new_match, name='new_match'),
    path('email/quarterly_roundup', retail_emails.quarterly_roundup, name='quarterly_roundup'),
    path('email/new_work_submission', retail_emails.new_work_submission, name='new_work_submission'),
    path('email/new_bounty_rejection', retail_emails.new_bounty_rejection, name='new_bounty_rejection'),
    path('email/new_bounty_acceptance', retail_emails.new_bounty_acceptance, name='new_bounty_acceptance'),
    path('email/bounty_expire_warning', retail_emails.bounty_expire_warning, name='bounty_expire_warning'),
    path('email/bounty_feedback', retail_emails.bounty_feedback, name='bounty_feedback'),
    path('email/funder_stale', retail_emails.funder_stale, name='funder_stale'),
    path('email/start_work_expire_warning', retail_emails.start_work_expire_warning, name='start_work_expire_warning'),
    path('email/start_work_expired', retail_emails.start_work_expired, name='start_work_expired'),
    path('email/gdpr_reconsent', retail_emails.gdpr_reconsent, name='gdpr_reconsent'),
    path('email/new_tip/resend', retail_emails.resend_new_tip, name='resend_new_tip'),
    path('email/start_work_approved', retail_emails.start_work_approved, name='start_work_approved'),
    path('email/start_work_rejected', retail_emails.start_work_rejected, name='start_work_rejected'),
    path('email/start_work_new_applicant', retail_emails.start_work_new_applicant, name='start_work_new_applicant'),
    path(
        'email/start_work_applicant_about_to_expire',
        retail_emails.start_work_applicant_about_to_expire,
        name='start_work_applicant_about_to_expire'
    ),
    path(
        'email/start_work_applicant_expired',
        retail_emails.start_work_applicant_expired,
        name='start_work_applicant_expired'
    ),

    # Processing Endpoints
    re_path(r'^process_accesscode_request/(.*)$', process_accesscode_request, name='process_accesscode_request'),
    re_path(r'^process_faucet_request/(.*)$', process_faucet_request, name='process_faucet_request'),

    # Data Visualization Views
    re_path(r'^stats/$', dataviz_views.stats, name='stats'),
    re_path(r'^cohort/$', dataviz_views.cohort, name='cohort'),
    re_path(r'^funnel/$', dataviz_views.funnel, name='funnel'),
    re_path(r'^viz/?$', dataviz_d3_views.viz_index, name='viz_index'),
    re_path(r'^viz/sunburst/(.*)?$', dataviz_d3_views.viz_sunburst, name='viz_sunburst'),
    re_path(r'^viz/chord/(.*)?$', dataviz_d3_views.viz_chord, name='viz_chord'),
    re_path(r'^viz/steamgraph/(.*)?$', dataviz_d3_views.viz_steamgraph, name='viz_steamgraph'),
    re_path(r'^viz/circles/(.*)?$', dataviz_d3_views.viz_circles, name='viz_circles'),
    re_path(r'^viz/sankey/(.*)?$', dataviz_d3_views.viz_sankey, name='viz_sankey'),
    re_path(r'^viz/spiral/(.*)?$', dataviz_d3_views.viz_spiral, name='viz_spiral'),
    re_path(r'^viz/heatmap/(.*)?$', dataviz_d3_views.viz_heatmap, name='viz_heatmap'),
    re_path(r'^viz/calendar/(.*)?$', dataviz_d3_views.viz_calendar, name='viz_calendar'),
    re_path(r'^viz/draggable/(.*)?$', dataviz_d3_views.viz_draggable, name='viz_draggable'),
    re_path(r'^viz/scatterplot/(.*)?$', dataviz_d3_views.viz_scatterplot, name='viz_scatterplot'),
]
