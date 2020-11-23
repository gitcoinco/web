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
    base, index, mission_answer, mission_base, mission_index, mission_question, mission_state,
)

app_name = 'quadraticlands'

# TODO Zak - quadraticlands VS quadraticlands/ 
# possible solution - https://stackoverflow.com/questions/1596552/django-urls-without-a-trailing-slash-do-not-redirect

# upgraded to re_path so we don't pass random uri strings to the views for processing
# I'm leaving the path('s that were replaced on this commit for reference then I will clean this up on the next commit 
urlpatterns = [
    path('', index, name='quadraticlands'),
    path('mission', mission_index, name='mission'),
    path('claim', claim, name='claim_json'),
    path('set_mission_status', set_mission_status, name='set_mission_status'),
    
    re_path(r'^(?P<base>about|leaderboard|privacy|terms-of-service|mission_knowledge_intro|dashboard|faq)$', base, name='quadraticlands_base'),  
    # path('<str:base>', base, name='quadraticlands'),
    
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)$', mission_base, name='mission_base'),
    # path('mission/<str:mission_name>', mission_base, name='mission'),
    
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)/(?P<mission_state>intro|outro|claim|snapshot)$', mission_state, name='mission_state'),
    # path('mission/<str:mission_name>/<str:mission_state>', mission_state, name='mission_state'),
    
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)/question/(?P<question_num>1|2)$', mission_question, name='mission_question'),
    # path('mission/<str:mission_name>/<str:mission_state>/<int:question_num>', mission_question, name='mission_questions'),
    
    re_path(r'^mission/(?P<mission_name>knowledge|receive|use)/question/(?P<question_num>1|2)/(?P<answer>right|wrong|timeout)$', mission_answer, name='mission_answer'),
    # path('mission/<str:mission_name>/<str:mission_state>/<int:question_num>/<str:answer>', mission_answer, name='mission_answer'),
    ]
