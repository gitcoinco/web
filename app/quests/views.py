
import json
import logging
import random
import re
import time

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Profile
from kudos.models import BulkTransferCoupon, BulkTransferRedemption, Token
from marketing.mails import new_quest_request
from marketing.models import EmailSubscriber
from quests.helpers import (
    get_leaderboard, max_ref_depth, process_start, process_win, record_award_helper, record_quest_activity,
)
from quests.models import Quest, QuestAttempt, QuestPointAward
from quests.quest_types.example import details as example
from quests.quest_types.quiz_style import details as quiz_style
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

current_round_number = 2

def next_quest(request):
    """Render the Quests 'random' page."""

    if not request.user.is_authenticated:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    for quest in Quest.objects.filter(visible=True).order_by('?'):
        if not quest.is_beaten(request.user) and quest.is_unlocked_for(request.user):
            return redirect(quest.url)


def newquest(request):
    """Render the Quests 'new' page."""

    if not request.user.is_authenticated:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    answers = []
    questions = [{
        'question': '',
        'responses': ['','']
    }]
    if request.POST:

        questions = [{
            'question': ele,
            'seconds_to_respond': 30,
            'responses': [],
        } for ele in request.POST.getlist('question[]', [])]

        # multi dimensional array hack
        counter = 0
        answer_idx = 0
        answers = request.POST.getlist('answer[]',[])
        answer_correct = request.POST.getlist('answer_correct[]',[])
        seconds_to_respond = request.POST.getlist('seconds_to_respond[]',[])

        # continue building questions object
        for i in range(0, len(seconds_to_respond)):
            questions[i]['seconds_to_respond'] = int(seconds_to_respond[i])

        for answer in answers:
            if answer == '_DELIMITER_':
                answer_idx += 1
            else:
                questions[answer_idx]['responses'].append({
                    'answer': answer,
                    'correct': bool(answer_correct[counter] == "YES"),
                })
            counter += 1

        validation_pass = True
        try:
            enemy = Token.objects.get(pk=request.POST.get('enemy'))
            reward = Token.objects.get(pk=request.POST.get('reward'))
        except Exception as e:
            messages.error(request, 'Unable to find Kudos')
            validation_pass = False 

        if validation_pass:
            seconds_per_question = request.POST.get('seconds_per_question', 30)
            game_schema = {
              "intro": request.POST.get('description'),
              "rules": f"You will be battling a {enemy.humanized_name}. You will have as much time as you need to prep before the battle, but once the battle starts you will have only seconds per move (keep an eye on the timer in the bottom right; don't run out of time!).",
              "seconds_per_question": seconds_per_question,
              'est_read_time_mins': request.GET.get('est_read_time_mins', 20),
              "prep_materials": [
                {
                  "url": request.POST.get('reading_material_url'),
                  "title": request.POST.get('reading_material_name')
                }
              ]
            }
            game_metadata = {
              "enemy": {
                "art": enemy.img_url,
                "level": "1",
                "title": enemy.humanized_name
              }
            }

            try:
                quest = Quest.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    questions=questions,
                    game_schema=game_schema,
                    game_metadata=game_metadata,
                    kudos_reward=reward,
                    cooldown_minutes=request.POST.get('minutes'),
                    visible=False,
                    difficulty=request.POST.get('difficulty'),
                    style=request.POST.get('style'),
                    value=request.POST.get('points'),
                    creator=request.user.profile,
                    )
                new_quest_request(quest)
                messages.info(request, f'Quest submission received.  We will respond via email in a few business days.  In the meantime, feel free to test your new quest @ https://gitcoin.co{quest.url}')
            except Exception as e:
                logger.exception(e)
                messages.error(request, 'An unexpected error has occured')

    params = {
        'title': 'New Quest Application',
        'package': request.POST,
        'questions': questions,
        'answer_correct': request.POST.getlist('answer_correct[]',[]),
        'seconds_to_respond': request.POST.getlist('seconds_to_respond[]',[]),
        'answer': request.POST.getlist('answer[]',[]),
    }
    return TemplateResponse(request, 'quests/new.html', params)


def get_package_helper(quest_qs, request):
    return [(ele.is_unlocked_for(request.user), ele.is_beaten(request.user), ele.is_within_cooldown_period(request.user), ele) for ele in quest_qs]


def index(request):

    print(f" start at {round(time.time(),2)} ")
    query = request.GET.get('q', '')
    quests = []
    if query:
        quest_qs = Quest.objects.filter(visible=True).filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(questions__icontains=query) | Q(game_schema__icontains=query) | Q(game_metadata__icontains=query))
        quest_package = get_package_helper(quest_qs, request)
        package = ('Search', quest_package)
        quests.append(package)
    for diff in Quest.DIFFICULTIES:
        quest_qs = Quest.objects.filter(difficulty=diff[0], visible=True)
        quest_package = get_package_helper(quest_qs, request)
        package = (diff[0], quest_package)
        if quest_qs.exists():
            quests.append(package)

    print(f" phase2 at {round(time.time(),2)} ")
    rewards_schedule = []
    for i in range(0, max_ref_depth):
        reward_denominator = 2 ** i;
        layer = i if i else 'You'
        rewards_schedule.append({
                'layer': layer,
                'reward_denominator': reward_denominator,
                'reward_multiplier': 1/reward_denominator
            })

    print(f" phase3 at {round(time.time(),2)} ")
    attempt_count = QuestAttempt.objects.count()
    success_count = QuestAttempt.objects.filter(success=True).count()
    print(f" phase3.1 at {round(time.time(),2)} ")
    leaderboard = {}
    for i in range(1, current_round_number+1):
        leaderboard[i] = get_leaderboard(round_number=i)
    print(f" phase3.2 at {round(time.time(),2)} ")
    point_history = request.user.profile.questpointawards.all() if request.user.is_authenticated else QuestPointAward.objects.none()
    point_value = sum(point_history.values_list('value', flat=True))
    print(f" phase4 at {round(time.time(),2)} ")
    # community_created
    params = {
        'profile': request.user.profile if request.user.is_authenticated else None,
        'quests': quests,
        'avg_play_count': round(QuestAttempt.objects.count()/Quest.objects.count(), 1),
        'quests_attempts_total': QuestAttempt.objects.count(),
        'quests_total': Quest.objects.filter(visible=True).count(),
        'quests_attempts_per_day': abs(round(QuestAttempt.objects.count()/(QuestAttempt.objects.first().created_on-timezone.now()).days,1)),
        'total_visible_quest_count': Quest.objects.filter(visible=True).count(),
        'gitcoin_created': Quest.objects.filter(visible=True).filter(creator=Profile.objects.filter(handle='gitcoinbot').first()).count(),
        'community_created': Quest.objects.filter(visible=True).exclude(creator=Profile.objects.filter(handle='gitcoinbot').first()).count(),
        'country_count': 87,
        'email_count': EmailSubscriber.objects.count(),
        'attempt_count': attempt_count,
        'success_count': success_count,
        'success_ratio': int(success_count/attempt_count * 100),
        'user_count': QuestAttempt.objects.distinct('profile').count(),
        'leaderboard': leaderboard,
        'REFER_LINK': f'https://gitcoin.co/quests/?cb=ref:{request.user.profile.ref_code}' if request.user.is_authenticated else None,
        'rewards_schedule': rewards_schedule,
        'query': query,
        'selected_tab': 'Search' if query else 'Beginner',
        'title': f' {query.capitalize()} Quests',
        'point_history': point_history,
        'point_value': point_value, 
        'current_round_number': current_round_number,
        'avatar_url': '/static/v2/images/quests/orb.png',
        'card_desc': 'Gitcoin Quests is a fun, gamified way to learn about the web3 ecosystem, compete with your friends, earn rewards, and level up your decentralization-fu!',
    }

    print(f" phase5 at {round(time.time(),2)} ")
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

    if quest.style.lower() == 'quiz':
        return quiz_style(request, quest)
    elif quest.style == 'Example for Demo':
        return example(request, quest)
    else:
        raise Exception(f'Not supported quest style: {quest.style}')
