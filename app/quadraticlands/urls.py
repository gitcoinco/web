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
    about, claim, dashboard, faq, index, m_k_i, m_k_o, m_k_q_1, m_k_q_1_r, m_k_q_1_w, m_k_q_2, m_k_q_2_r, m_k_q_2_w,
    privacy, terms,
)

app_name = 'quadraticlands'

# I am still working on the append-slash issue - there is Django middleware to solve this problem but it has to be implemented a the app level (gitcoin.co)
# so I am looking for another solution - https://stackoverflow.com/questions/1596552/django-urls-without-a-trailing-slash-do-not-redirect

# @Richard, please feel free to adjust these as necessary - 
# it really doesn't matter much how we set these up and there are many ways it can be done so it's just a matter of preference 
# i used m_k_q style because it was going to be very long to write it out and you can see now more clearly the relationship between views.py and urls.py 

urlpatterns = [
    path('', index , name='quadraticlands'),
    path('about', about, name='about'),
    path('faq', faq, name='faq'),
    path('terms', terms, name='terms'),
    path('demo', claim, name='demo-claim'),
    path('dashboard', dashboard, name='dashboard'),
    path('mission/knowledge/intro', m_k_i, name='mission_knowledge_intro'),
    path('mission/knowledge/question/1', m_k_q_1, name='mission_knowledge_question_1'),
    path('mission/knowledge/question/1', m_k_q_1_w, name='mission_knowledge_question_1_wrong'),
    path('mission/knowledge/question/1', m_k_q_1_r, name='mission_knowledge_question_1_right'),
    path('mission/knowledge/question/2', m_k_q_2, name='mission_knowledge_question_2'),
    path('mission/knowledge/question/1', m_k_q_2_w, name='mission_knowledge_question_2_wrong'),
    path('mission/knowledge/question/1', m_k_q_2_r, name='mission_knowledge_question_2_right'),
    path('mission/knowledge/outro', m_k_o, name='mission_knowledge_outro'),
    ]
