# -*- coding: utf-8 -*-
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
import cgi
import re

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from marketing.models import Alumni
from requests_oauthlib import OAuth2Session


def get_github_user_profile(token):
    github = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        token=token,
    )

    creds = github.get('https://api.github.com/user').json()
    print(creds)
    return creds


def strip_html(html):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    no_tags = tag_re.sub('', html)
    txt = cgi.escape(no_tags)

    return txt


def strip_double_chars(txt, char=' '):
    new_txt = txt.replace(char+char, char)
    if new_txt == txt:
        return new_txt
    return strip_double_chars(new_txt, char)


def build_stat_results():
    from dashboard.models import Bounty

    """Buidl the results page context."""
    context = {
        'active': 'results',
        'title': _('Results'),
    }

    baes_bounties = Bounty.objects.current()
    context['alumni_count'] = Alumni.objects.count()
    context['count_open'] = baes_bounties.filter(network='mainnet', idx_status__in=['open']).count()
    context['count_started'] = baes_bounties.filter(network='mainnet', idx_status__in=['started', 'submitted']).count()
    context['count_done'] = baes_bounties.filter(network='mainnet', idx_status__in=['done']).count()

    # Bounties
    # TODO: make this info dynamic
    context['universe_total_usd'] = 160000  # TODO
    context['bounty_abandonment_rate'] = '9.5%'  # TODO
    context['bounty_average_turnaround'] = '2.1 Weeks'  
    context['hourly_rate_distribution'] = '$15 - $120' 
    context['bounty_claimed_completion_rate'] = '98%'  
    context['bounty_median_pickup_time'] = '1.5'  

    return context
