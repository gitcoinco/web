import json
import logging
import random
import re

from django.contrib import messages
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Activity
from kudos.models import BulkTransferCoupon
from kudos.views import get_profile
from quests.models import Quest, QuestAttempt
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

def record_quest_activity(quest, associated_profile, event_name, override_created=None):
    kwargs = {
        'created_on': timezone.now() if not override_created else override_created,
        'activity_type': event_name,
        'profile': associated_profile,
        'metadata': {
            'quest_url': quest.url,
            'quest_title': quest.title,
            'quest_reward': quest.enemy_img_url if quest.enemy_img_url else None,
        }
    }

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logger.exception(e)


# Create your views here.
def index(request):

    quests = [(ele.is_unlocked_for(request.user), ele.is_beaten(request.user), ele.is_within_cooldown_period(request.user), ele) for ele in Quest.objects.filter(visible=True)]
    leaderboard = QuestAttempt.objects.filter(success=True).order_by('profile').values_list('profile__handle').annotate(amount=Count('quest', distinct=True)).order_by('-amount')
    params = {
        'quests': quests,
        'leaderboard': leaderboard,
        'title': 'Quests on Gitcoin',
        'card_desc': 'Use Gitcoin to learn about the web3 ecosystem, earn rewards, and level up while you do it!',
    }
    return TemplateResponse(request, 'quests/index.html', params)

@csrf_exempt
@ratelimit(key='ip', rate='10/s', method=ratelimit.UNSAFE, block=True)
def details(request, obj_id, name):

    if not request.user.is_authenticated and request.GET.get('login'):
        return redirect('/login/github?next=' + request.get_full_path())

    """Render the Kudos 'detail' page."""
    if not re.match(r'\d+', obj_id):
        raise ValueError(f'Invalid obj_id found.  ID is not a number:  {obj_id}')

    try:
        quest = Quest.objects.get(pk=obj_id)
        if not quest.is_unlocked_for(request.user):
            messages.info(request, 'This quest is locked. Try again after you have unlocked it')
            return redirect('/quests');
    except:
        raise Http404

    try:
        payload = json.loads(request.body)
        qn = payload.get('question_number')
        can_continue = True
        did_win = False
        prize_url = False
        if qn is not None and request.user.is_authenticated:
            save_attempt = qn == 0
            if save_attempt:
                QuestAttempt.objects.create(
                    quest=quest,
                    success=False,
                    profile=request.user.profile,
                    state=0,
                    )
                record_quest_activity(quest, request.user.profile, 'played_quest')
            else:
                qas = QuestAttempt.objects.filter(quest=quest, profile=request.user.profile, state=(qn-1), created_on__gt=(timezone.now()-timezone.timedelta(minutes=5)))
                qa = qas.order_by('-pk').first()
                this_question = quest.questions[qn-1]
                correct_answers = [ele['answer'] for ele in this_question['responses'] if ele['correct']]
                their_answers = payload.get('answers')
                did_they_do_correct = set(correct_answers) == set(their_answers) or (this_question.get('any_correct', False) and len(their_answers))
                can_continue = did_they_do_correct
                if can_continue:
                    qa.state += 1
                    qa.save()
                did_win = can_continue and len(quest.questions) <= qn
                if did_win:
                    record_quest_activity(quest, request.user.profile, 'beat_quest')
                    btc = BulkTransferCoupon.objects.create(
                        token=quest.kudos_reward,
                        num_uses_remaining=1,
                        num_uses_total=1,
                        current_uses=0,
                        secret=random.randint(10**19, 10**20),
                        comments_to_put_in_kudos_transfer=f"Congrats on beating the '{quest.title}' Gitcoin Quest",
                        sender_profile=get_profile('gitcoinbot'),
                        )
                    prize_url = btc.url
                    qa.success=True
                    qa.save()

            response = {
                "question": quest.questions_safe(qn),
                "can_continue": can_continue,
                "did_win": did_win,
                "prize_url": prize_url,
            }
            return JsonResponse(response)
    except Exception as e:
        print(e)
        pass

    if quest.is_within_cooldown_period(request.user):
        if request.user.is_staff:
            messages.info(request, f'You are within this quest\'s {quest.cooldown_minutes} min cooldown period. Normally wed send you to another quest.. but..  since ur staff u can try it!')
        else:
            messages.info(request, f'You are within this quest\'s {quest.cooldown_minutes} min cooldown period. Try again later.')
            return redirect('/quests');
    elif quest.is_beaten(request.user):
        if request.user.is_staff:
            messages.info(request, 'You have beaten this quest.  Normally wed send you to another quest.. but.. since ur staff u can try it again!')
        else:
            messages.info(request, 'Youve already conquered this quest! Congrats.')
            return redirect('/quests');

    params = {
        'quest': quest,
        'hide_col': True,
        'body_class': 'quest_battle',
        'title': "Quest: " + quest.title + (f" (and win a *{quest.kudos_reward.humanized_name}* Kudos)" if quest.kudos_reward else ""),
        'avatar_url': quest.enemy_img_url,
        'card_desc': quest.description,
        'quest_json': quest.to_json_dict(exclude="questions"),
    }
    return TemplateResponse(request, 'quests/quest.html', params)
