
import json
import logging
import random
import re

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


def details(request, quest):
    # return params
    prize_url = ''
    active_attempt = get_active_attempt_if_any(request.user, quest)
    if request.POST.get('start'):
        # game started
        if not request.user.is_authenticated:
            return redirect('/login/github')

        messages.info(request, f'Quest started.  Journey Forth')
        process_start(request, quest)
    elif request.POST.get('win'):
        # game won
        messages.info(request, f'You win.. Congrats')
        prize_url = process_win(request, active_attempt)
    elif request.POST.get('lose'):
        # game lost
        messages.info(request, f'You lose. Try again soon.')
        return redirect('/quests')
    else:
        if active_attempt:
            messages.info(request, f'You lose. Try again after the cooltown period.')
            return redirect('/quests')

    attempts = quest.attempts.filter(profile=request.user.profile) if request.user.is_authenticated else quest.attempts.none()
    params = get_base_quest_view_params(request.user, quest)
    params['prize_url'] = prize_url
    params['started'] = request.POST.get('start', '')
    response = TemplateResponse(request, 'quests/types/example.html', params)
    return response
