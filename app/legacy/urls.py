# -*- coding: utf-8 -*-
"""Handle legacy URLs.

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

from dashboard.views import bounty_details, fulfill_bounty, kill_bounty, process_bounty, sync_web3

app_name = 'legacy'
urlpatterns = [
    # Path changed during migration to standard bounties.
    re_path(r'^bounty/claim/?', fulfill_bounty, name='legacy_claim_bounty'),
    re_path(r'^funding/claim/?', fulfill_bounty, name='legacy_claim_funding'),
    re_path(r'^funding/fulfill/?', fulfill_bounty, name='legacy_claim_funding1'),
    re_path(r'^bounty/fulfill/?', fulfill_bounty, name='legacy_claim_funding2'),
    re_path(r'^funding/clawback/?', kill_bounty, name='legacy_clawback_expired_bounty'),

    # Endpoints that need to support old logic.
    # Bounties
    re_path(r'^bounty/process/?', process_bounty, name='legacy_process_bounty'),
    re_path(r'^funding/process/?', process_bounty, name='legacy_process_funding'),
    re_path(r'^bounty/details/?', bounty_details, name='legacy_bounty_details'),
    re_path(r'^funding/details/?', bounty_details, name='legacy_funding_details'),
    re_path(r'^issue/(?P<ghuser>.*)/(?P<ghrepo>.*)/(?P<ghissue>.*)', bounty_details, name='legacy_issue_details_new2'),
    # sync methods
    re_path(r'^sync/web3', sync_web3, name='legacy_sync_web3'),
]
