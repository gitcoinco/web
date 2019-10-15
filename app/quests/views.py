
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
    get_leaderboard, max_ref_depth, process_start, process_win, record_award_helper, record_quest_activity,
)
from quests.models import Quest, QuestAttempt, QuestPointAward
from quests.quest_types.quiz_style import details as quiz_style
from quests.quest_types.example import details as example
from ratelimit.decorators import ratelimit


# Create your views here.
def index(request):

    quests = []
    for diff in Quest.DIFFICULTIES:
        quest_qs = Quest.objects.filter(difficulty=diff[0], visible=True)
        quest_package = [(ele.is_unlocked_for(request.user), ele.is_beaten(request.user), ele.is_within_cooldown_period(request.user), ele) for ele in quest_qs]
        package = (diff[0], quest_package)
        if quest_qs.exists():
            quests.append(package)

    rewards_schedule = []
    for i in range(0, max_ref_depth):
        reward_denominator = 2 ** i;
        layer = i if i else 'You'
        rewards_schedule.append({
                'layer': layer,
                'reward_denominator': reward_denominator,
                'reward_multiplier': 1/reward_denominator
            })

    attempt_count = QuestAttempt.objects.count()
    success_count = QuestAttempt.objects.filter(success=True).count()
    leaderboard = get_leaderboard()
    point_history = request.user.profile.questpointawards.all() if request.user.is_authenticated else QuestPointAward.objects.none()
    point_value = sum(point_history.values_list('value', flat=True))
    params = {
        'profile': request.user.profile if request.user.is_authenticated else None,
        'quests': quests,
        'attempt_count': attempt_count,
        'success_count': success_count,
        'success_ratio': int(success_count/attempt_count * 100),
        'user_count': QuestAttempt.objects.distinct('profile').count(),
        'leaderboard': leaderboard[0],
        'leaderboard_hero': leaderboard[1],
        'REFER_LINK': f'https://gitcoin.co/quests/?cb=ref:{request.user.profile.ref_code}' if request.user.is_authenticated else None,
        'rewards_schedule': rewards_schedule,
        'title': 'Quests',
        'point_history': point_history,
        'point_value': point_value,
        'avatar_url': '/static/v2/images/quests/orb.png',
        'card_desc': 'Gitcoin Quests is a fun, gamified way to learn about the web3 ecosystem, compete with your friends, earn rewards, and level up your decentralization-fu!',
    }
    return TemplateResponse(request, 'quests/index.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='10/s', method=ratelimit.UNSAFE, block=True)
def details(request, obj_id, name):
    """Render the Quests 'detail' page."""

    if not re.match(r'\d+', obj_id):
        raise ValueError(f'Invalid obj_id found.  ID is not a number:  {obj_id}')

    try:
        quest = Quest.objects.get(pk=obj_id)
        if not quest.is_unlocked_for(request.user):
            messages.info(request, 'This quest is locked. Try again after you have unlocked it')
            return redirect('/quests')
    except:
        raise Http404

    if quest.style == 'quiz':
        return quiz_style(request, quest)
    elif quest.style == 'Example for Demo':
        return example(request, quest)
    else:
        raise Exception(f'Not supported quest style: {quest.style}')
