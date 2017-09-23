"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
import retail.views
import dashboard.views
import dashboard.helpers
import retail.emails
import tdi.views

from django.conf.urls import (
    handler400,
    handler403,
    handler404,
    handler500
)
from dashboard.router import router

urlpatterns = [

    # brochureware views
    url(r'^about/?', retail.views.about, name='about'),
    url(r'^get/?', retail.views.get_gitcoin, name='get_gitcoin'),
    url(r'^$', retail.views.index, name='index'),

    # dashboard views
    url(r'^dashboard/?', dashboard.views.dashboard, name='dashboard'),
    url(r'^explorer/?', dashboard.views.dashboard, name='explorer'),
    url(r'^search/save?', dashboard.views.save_search, name='save_search'),
    url(r'^bounty/sync_web3/?', dashboard.views.sync_web3, name='sync_web3'),
    url(r'^bounty/new/?', dashboard.views.new_bounty, name='new_bounty'),
    url(r'^bounty/claim/?', dashboard.views.claim_bounty, name='claim_bounty'),
    url(r'^bounty/process/?', dashboard.views.process_bounty, name='process_bounty'),
    url(r'^bounty/details/?', dashboard.views.bounty_details, name='bounty_details'),
    url(r'^helpers/get_title?', dashboard.helpers.title, name='helpers_title'),
    url(r'^helpers/get_keywords?', dashboard.helpers.keywords, name='helpers_keywords'),

    #token distribution event
    url(r'^whitepaper/accesscode?', tdi.views.whitepaper_access, name='whitepaper_access'),
    url(r'^whitepaper/?', tdi.views.whitepaper_new, name='whitepaper'),


    # api views
    url(r'^api/v0.1/', include(router.urls)),

    # admin views
    url(r'^_administration/?', admin.site.urls, name='admin'),
    url(r'^_administration/email/new_bounty$', retail.emails.new_bounty, name='new_bounty'),
    url(r'^_administration/email/roundup$', retail.emails.roundup, name='roundup'),
    url(r'^_administration/email/new_bounty_claim$', retail.emails.new_bounty_claim, name='new_bounty_claim'),
    url(r'^_administration/email/new_bounty_rejection$', retail.emails.new_bounty_rejection, name='new_bounty_rejection'),
    url(r'^_administration/email/new_bounty_acceptance$', retail.emails.new_bounty_acceptance, name='new_bounty_acceptance'),
    url(r'^_administration/email/bounty_expire_warning$', retail.emails.bounty_expire_warning, name='bounty_expire_warning'),

]

handler403 = 'retail.views.handler403'
handler404 = 'retail.views.handler404'
handler500 = 'retail.views.handler500'
handler400 = 'retail.views.handler400'
