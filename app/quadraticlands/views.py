# -*- coding: utf-8 -*-
"""Define the quadraticlands views.

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

import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from quadraticlands.decorators import is_staff_or_ql_tester
from quadraticlands.helpers import (
    get_coupon_code, get_FAQ, get_initial_dist, get_initial_dist_breakdown, get_mission_status, get_stewards,
)
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)


@is_staff_or_ql_tester
def index(request):
    '''render template for base index page'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, 'quadraticlands/index.html', context)


@is_staff_or_ql_tester
def base(request, base):
    '''render templates for /quadraticlands/'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    if base == 'faq':
        context.update(get_FAQ(request))
    return TemplateResponse(request, f'quadraticlands/{base}.html', context)


@is_staff_or_ql_tester
@login_required
def base_auth(request, base):
    '''render templates for /quadraticlands/'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    if base == 'stewards':
        context.update(get_stewards())
    return TemplateResponse(request, f'quadraticlands/{base}.html', context)


@is_staff_or_ql_tester
@login_required
def mission_index(request):
    '''render quadraticlands/mission/index.html'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, 'quadraticlands/mission/index.html', context)


@is_staff_or_ql_tester
@login_required
def mission_base(request, mission_name):
    '''used to handle quadraticlands/<mission_name>'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    if mission_name == 'use' and game_status["proof_of_knowledge"] == False:
        return redirect('/quadraticlands/mission')
    if mission_name == 'receive': 
        if game_status["proof_of_knowledge"] == False or game_status["proof_of_use"] == False:
            return redirect('/quadraticlands/mission')
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/index.html', context)

@is_staff_or_ql_tester
@login_required
def dashboard_index(request):
    '''render quadraticlands/dashboard/index.html'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, 'quadraticlands/dashboard/index.html', context)


@is_staff_or_ql_tester
@login_required
def mission_state(request, mission_name, mission_state):
    '''quadraticlands/<mission_name>/<mission_state>'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    if mission_state == 'delegate':
        context.update(get_stewards())
    if mission_state == 'claim':
        if game_status['proof_of_knowledge'] == False or game_status["proof_of_use"] == False:
            return redirect('/quadraticlands/mission')
    if mission_state == 'claim':
        context.update(get_initial_dist_breakdown(request))
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/{mission_state}.html', context)


@is_staff_or_ql_tester
@login_required
def mission_question(request, mission_name, question_num):
    '''Used to handle quadraticlands/<mission_name>/<mission_state>/<question_num>'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/question_{question_num}.html', context)


@is_staff_or_ql_tester
@login_required
def mission_answer(request, mission_name, question_num, answer):
    '''Used to handle quadraticlands/<mission_name>/<mission_state>/<question_num>/<answer>'''
    context, game_status = get_initial_dist(request), get_mission_status(request)
    context.update(game_status)
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/question_{question_num}_{answer}.html', context)


@is_staff_or_ql_tester
def workstream_index(request):
    '''Use to render quadraticlands/workstream/index.html'''
    return TemplateResponse(request, 'quadraticlands/workstream/index.html')


@is_staff_or_ql_tester
def workstream_base(request, stream_name):
    '''Used to render quadraticlands/workstream/<stream_name>.html'''
    return TemplateResponse(request, f'quadraticlands/workstream/{stream_name}.html')


@is_staff_or_ql_tester
@login_required
@require_POST
@csrf_protect
def mission_process(request, mission_name, question_num):
    answer = request.POST.get('answer')
    if mission_name == 'knowledge' and question_num == '1' and answer == '2':
        return redirect(reverse('quadraticlands:mission_answer', args=(mission_name, question_num, 'right')))
    elif mission_name == 'knowledge' and question_num == '2' and answer == '4':
        return redirect(reverse('quadraticlands:mission_answer', args=(mission_name, question_num, 'right')))
    else:
        return redirect(reverse('quadraticlands:mission_answer', args=(mission_name, question_num, 'wrong')))


@is_staff_or_ql_tester
@login_required
def mission_postcard(request):
    '''Used to handle quadraticlands/<mission_name>/<mission_state>/<question_num>'''
    attrs = {
        'front_frame': ['1', '2', '3', '4', '5', '6'],
        'front_background': ['a', 'b', 'c', 'd', 'e'],
        'back_background': ['a', 'b', 'c', 'd', 'e'],
        'color': ['light', 'dark'],
    }
    context = {
        'attrs': attrs,
    }
    return TemplateResponse(request, f'quadraticlands/mission/postcard/postcard.html', context)


@is_staff_or_ql_tester
@ratelimit(key='ip', rate='4/s', method=ratelimit.UNSAFE, block=True)
def mission_postcard_svg(request):
    import xml.etree.ElementTree as ET

    from django.http import HttpResponse

    width = 100
    height = 100
    viewBox = request.GET.get('viewbox', '')
    tags = ['{http://www.w3.org/2000/svg}style']
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    prepend = f'''<?xml version="1.0" encoding="utf-8"?>
<svg width="{width}%" height="{height}%" viewBox="0 0 1400 500" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
'''
    postpend = '''
</svg>
'''

    package = request.GET.dict()
    file = 'assets/v2/images/quadraticlands/postcard.svg'
    with open(file) as file:
        elements = []
        tree = ET.parse(file)
        for item in tree.getroot():
            output = ET.tostring(item).decode('utf-8')

            _id = item.attrib.get('id')
            include_item = _id == 'include'
            if _id == 'text':

                # get text
                replace_text = package.get('text')

                # chop up the text by word length to create line breaks.
                line_words_length = int(request.GET.get('line_words_length', 8))
                include_item = True
                end_wrap = '</tspan>'
                words = replace_text.split(' ')
                new_words = []
                line_offset = 0
                line_counter_for_newline_insert = 0
                for i in range(0, len(words)):
                    line_counter_for_newline_insert += 1
                    if words[i] == 'NEWLINE':
                        line_counter_for_newline_insert = 0
                    insert_newline = line_counter_for_newline_insert % line_words_length == 0
                    if words[i] == 'NEWLINE':
                        insert_newline = True
                    if insert_newline:
                        line_offset += 1

                    y = 26 + (line_offset) * 26
                    start_wrap = f'<tspan x="0" y="{y}">'

                    if i == 0:
                        new_words.append(start_wrap)
                    if insert_newline:
                        new_words.append(end_wrap)
                        new_words.append(start_wrap)
                    if words[i] != 'NEWLINE':
                        new_words.append(words[i])
                    if i == (len(words) - 1):
                        new_words.append(end_wrap)

                # actually insert the text
                replace_text = " ".join(new_words)
                output = output.replace('POSTCARD_TEXT_GOES_HERE', replace_text)
                replace_color = '#1a103d' if request.GET.get('color','') == 'light' else '#FFFFFF'
                output = output.replace('POSTCARD_COLOR_GOES_HERE', replace_color)
            if _id:
                val = _id.split(":")[-1]
                key = _id.split(":")[0]
                if val == package.get(key):
                    include_item = True
            if include_item:
                elements.append(output)
        output = prepend + "".join(elements) + postpend

        response = HttpResponse(output, content_type='image/svg+xml')
        return response


@login_required
@ratelimit(key='ip', rate='4/s', method=ratelimit.UNSAFE, block=True)
def mission_lore(request):
    from perftools.models import JSONStore
    data = JSONStore.objects.get(view='QLLORE', key='QLLORE').data
    MOLOCH_COMIC_LINK = data['MOLOCH_COMIC_LINK']
    QL_SONG_LINK = data['QL_SONG_LINK']
    params = {
        'MOLOCH_COMIC_LINK': MOLOCH_COMIC_LINK,
        'QL_SONG_LINK': QL_SONG_LINK,
    }
    return TemplateResponse(request, f'quadraticlands/mission/lore/index.html', params)


@login_required
@ratelimit(key='ip', rate='4/s', method=ratelimit.UNSAFE, block=True)
def mission_schwag(request):

    context = {
        'coupon_code': get_coupon_code(request)
    }

    return TemplateResponse(request, f'quadraticlands/mission/schwag/index.html', context)


def handler403(request, exception=None):
    return error(request, 403)


def handler404(request, exception=None):
    return error(request, 404)


def handler500(request, exception=None):
    return error(request, 500)


def handler400(request, exception=None):
    return error(request, 400)


def error(request, code):
    context = {
        'code': code,
        'title': "Error {}".format(code)
    }
    return_as_json = 'api' in request.path

    if return_as_json:
        return JsonResponse(context, status=code)
    return TemplateResponse(request, f'quadraticlands/error.html', context, status=code)
