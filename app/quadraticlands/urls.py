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

from quadraticlands.helpers import claim, set_mission_status
from quadraticlands.views import (
    base, dashboard_index, index, mission_answer, mission_base, mission_index, mission_question, mission_state,
    proposal,
)

app_name = 'quadraticlands'

urlpatterns = [
    
    path('', index, name='quadraticlands'),
    path('/', index, name='quadraticlands'),
    path('mission', mission_index, name='mission'),
    path('dashboard', dashboard_index, name='dashboard'),
    path('claim', claim, name='claim_json'),
    path('set_mission_status', set_mission_status, name='set_mission_status'),
    path('proposal/<int:proposal_id>/', proposal, name='proposal'),
    re_path(r'^(?P<base>about|leaderboard|privacy|terms-of-service|mission_knowledge_intro|dashboard|faq|web3|particletest|particletest2|proposal)$', base, name='quadraticlands_base'),
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)$', mission_base, name='mission_base'),
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)/(?P<mission_state>intro|outro|claim|snapshot|vote)$', mission_state, name='mission_state'),
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)/question/(?P<question_num>1|2)$', mission_question, name='mission_question'),
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)/question/(?P<question_num>1|2)/(?P<answer>right|wrong|timeout)$', mission_answer, name='mission_answer'),
    
    ]
