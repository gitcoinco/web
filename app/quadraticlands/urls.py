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

from quadraticlands.views import (
    about, claim, dashboard, faq, index, mission, mission_end, mission_knowledge_index, mission_knowledge_intro,
    mission_knowledge_outro, mission_knowledge_question_1, mission_knowledge_question_1_right,
    mission_knowledge_question_1_timeout, mission_knowledge_question_1_wrong, mission_knowledge_question_2,
    mission_knowledge_question_2_right, mission_knowledge_question_2_timeout, mission_knowledge_question_2_wrong,
    mission_recieve_index, mission_recieve_outro, mission_revieve_claim, mission_revieve_claimed,
    mission_revieve_claiming, mission_use_index, mission_use_outro, mission_use_snapshot, privacy, terms,
)

app_name = 'quadraticlands'

# I am still working on the append-slash issue - there is Django middleware to solve this problem but it has to be implemented a the app level (gitcoin.co)
# so I am looking for another solution - https://stackoverflow.com/questions/1596552/django-urls-without-a-trailing-slash-do-not-redirect
    
# @zach : need another route /mission 
# should be a helper route with no view involved 
# that redirects based on user mission status in database to 
# 0 = knowledge
# 1 = recieve
# 2 = use

urlpatterns = [
    path('', index , name='quadraticlands'),
    path('about', about, name='about'),
    path('faq', faq, name='faq'),
    path('terms', terms, name='terms'),
    path('demo', claim, name='demo-claim'),
    path('dashboard', dashboard, name='dashboard'),

    path('mission', mission, name='mission'),

    path('mission/knowledge', mission_knowledge_index, name='mission_knowledge_index'),
    path('mission/knowledge/intro', mission_knowledge_intro, name='mission_knowledge_intro'),
    path('mission/knowledge/question/1', mission_knowledge_question_1, name='mission_knowledge_question_1'),
    path('mission/knowledge/question/1/right', mission_knowledge_question_1_right, name='mission_knowledge_question_1_right'),
    path('mission/knowledge/question/1/wrong', mission_knowledge_question_1_wrong, name='mission_knowledge_question_1_wrong'),
    path('mission/knowledge/question/1/timeout', mission_knowledge_question_1_timeout, name='mission_knowledge_question_1_timeout'),
    path('mission/knowledge/question/2', mission_knowledge_question_2, name='mission_knowledge_question_2'),
    path('mission/knowledge/question/2/right', mission_knowledge_question_2_right, name='mission_knowledge_question_2_right'),
    path('mission/knowledge/question/2/wrong', mission_knowledge_question_2_wrong, name='mission_knowledge_question_2_wrong'),
    path('mission/knowledge/question/2/timeout', mission_knowledge_question_2_timeout, name='mission_knowledge_question_2_timeout'),
    path('mission/knowledge/outro', mission_knowledge_outro, name='mission_knowledge_outro'),

    path('mission/recieve', mission_recieve_index, name='mission_recieve_index'),
    path('mission/recieve/claim', mission_revieve_claim, name='mission_revieve_claim'),
    path('mission/recieve/claiming', mission_revieve_claiming, name='mission_revieve_claiming'),
    path('mission/recieve/claimed', mission_revieve_claimed, name='mission_revieve_claimed'),
    path('mission/recieve/outro', mission_recieve_outro, name='mission_recieve_outro'),

    path('mission/use', mission_use_index, name='mission_use_index'),
    path('mission/use/snapshot', mission_use_snapshot, name='mission_use_snapshot'),
    path('mission/use/outro', mission_use_outro, name='mission_use_outro'),

    path('mission/end', mission_end, name='mission_end'),

        
    ]
