
import json
import logging
import random
import re
from json.decoder import JSONDecodeError

from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from kudos.models import BulkTransferCoupon, BulkTransferRedemption, Token
from quests.helpers import (
    get_active_attempt_if_any, get_base_quest_view_params, get_leaderboard, max_ref_depth, process_start, process_win,
    record_award_helper, record_quest_activity,
)
from quests.models import Quest, QuestAttempt, QuestPointAward
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def escape(text):
    for key, val in html_escape_table.items():
        text = text.replace(key, val)
    return text


def unescape(text):
    for key, val in html_escape_table.items():
        text = text.replace(val, key)
    return text


def details(request, quest):

    time_per_answer = quest.game_schema.get('seconds_per_question', 30)
    time_per_answer_buffer = 5

    if not request.user.is_authenticated and request.GET.get('login'):
        return redirect('/login/github/?next=' + request.get_full_path())

    # process form submission
    try:
        if request.body or request.GET.get('answers'):
            payload = {}
            try:
                payload = json.loads(request.body)
            except JSONDecodeError:
                payload = json.loads(request.GET['answers'])

            qn = payload.get('question_number')
            can_continue = True
            did_win = False
            prize_url = False
            if qn is not None and request.user.is_authenticated:
                save_attempt = qn == 0
                reason = ''
                if save_attempt:
                    process_start(request, quest)
                else:
                    qa = get_active_attempt_if_any(request.user, quest, state=(qn-1))
                    this_question = quest.questions[qn-1]
                    correct_answers = [ele['answer'] for ele in this_question['responses'] if ele['correct']]
                    their_answers = [unescape(ele) for ele in payload.get('answers')]
                    this_time_per_answer = time_per_answer
                    answer_level_seconds_to_respond = payload.get('seconds_to_respond', None)
                    if answer_level_seconds_to_respond:
                        this_time_per_answer = answer_level_seconds_to_respond
                    time_used = (timezone.now() - qa.modified_on).seconds
                    is_out_of_time = time_used > this_time_per_answer + time_per_answer_buffer
                    if is_out_of_time:
                        # fix for silly issue where the time used is almost exactly
                        # 24 hours off.  cant figure out exactly why but it happens.
                        if time_used > 86390 and time_used <= 86400:
                            is_out_of_time = False
                    did_they_do_correct = set(correct_answers) == set(their_answers) or (this_question.get('any_correct', False) and len(their_answers))
                    can_continue = did_they_do_correct and not is_out_of_time
                    if not did_they_do_correct:
                        reason = 'not correct'
                    if is_out_of_time:
                        reason = f'out of time- used {time_used} s from qa {qa.pk} '
                    if can_continue:
                        qa.state += 1
                        qa.save()
                    did_win = can_continue and len(quest.questions) <= qn
                    if did_win:
                        prize_url = process_win(request, qa)
                    qa.save()

                response = {
                    "question": quest.questions_safe(qn),
                    "can_continue": can_continue,
                    "did_win": did_win,
                    "prize_url": prize_url,
                    'reason': reason,
                }
                response = JsonResponse(response)
                #response['X-Frame-Options'] = x_frame_option
                return response

    except Exception as e:
        logger.exception(e)
        pass

    # make sure that cooldown period is respected
    override_cooldown = request.user.is_staff and request.GET.get('force', False)
    if quest.is_within_cooldown_period(request.user) and not override_cooldown:
        cooldown_time_left = (timezone.now() - quest.last_failed_attempt(request.user).created_on).seconds
        cooldown_time_left = round((quest.cooldown_minutes - cooldown_time_left/60),1)
        messages.info(request, f'You are within this quest\'s {quest.cooldown_minutes} min cooldown period. Try again in {cooldown_time_left} mins.')
        return redirect('/quests');

    # return params
    attempts = quest.attempts.filter(profile=request.user.profile) if request.user.is_authenticated else quest.attempts.none()
    params = get_base_quest_view_params(request.user, quest)
    response = TemplateResponse(request, 'quests/types/quiz_style.html', params)
    #response['X-Frame-Options'] = x_frame_option
    return response
