
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
from django.templatetags.static import static
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Profile
from kudos.models import BulkTransferCoupon, BulkTransferRedemption, Token
from marketing.mails import new_quest_request, send_user_feedback
from marketing.models import EmailSubscriber
from quests.helpers import (
    get_leaderboard, max_ref_depth, process_start, process_win, record_award_helper, record_quest_activity,
)
from quests.models import Quest, QuestAttempt, QuestPointAward, video_enabled_backgrounds
from quests.quest_types.example import details as example
from quests.quest_types.quiz_style import details as quiz_style
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

current_round_number = 6


def next_quest(request):
    """Render the Quests 'random' page."""

    if not request.user.is_authenticated:
        login_redirect = redirect('/login/github/?next=' + request.get_full_path())
        return login_redirect

    for quest in Quest.objects.filter(visible=True).order_by('?'):
        if not quest.is_beaten(request.user) and quest.is_unlocked_for(request.user):
            return redirect(quest.url)

    messages.info(request, f'You have beaten every available quest!')
    return redirect('/quests')


def editquest(request, pk=None):
    """Render the Quests 'new/edit' page."""

    # preamble
    post_pk = request.POST.get('pk')
    if not pk and post_pk:
        pk = post_pk

    # auth
    if not request.user.is_authenticated:
        login_redirect = redirect('/login/github/?next=' + request.get_full_path())
        return login_redirect

    quest = None
    if pk:
        try:
            quest = Quest.objects.get(pk=pk)
            if not request.user.is_authenticated:
                raise Exception('no')
            if quest.creator != request.user.profile:
                if not request.user.is_staff:
                    raise Exception('no')
        except:
            raise Http404

    # setup vars
    package = request.POST.copy()
    answers = []
    questions = [{
        'question': '',
        'responses': ['','']
    }]

    #handle submission
    if package:

        questions = [{
            'question': ele,
            'seconds_to_respond': 30,
            'responses': [],
        } for ele in package.getlist('question[]', [])]

        # multi dimensional array hack
        counter = 0
        answer_idx = 0

        answers = package.getlist('answer[]',[])
        answer_correct = package.getlist('answer_correct[]',[])
        seconds_to_respond = package.getlist('seconds_to_respond[]',[])
        points = abs(int(float(package.get('points'))))

        # continue building questions object
        for i in range(0, len(seconds_to_respond)):
            questions[i]['seconds_to_respond'] = abs(int(seconds_to_respond[i]))

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
        reward = None
        try:
            enemy = Token.objects.get(pk=package.get('enemy'))
            if package.get('reward'):
                reward = Token.objects.get(pk=package.get('reward'))
        except Exception as e:
            messages.error(request, 'Unable to find Kudos')
            validation_pass = False

        if validation_pass:
            seconds_per_question = package.get('seconds_per_question', 30)
            game_schema = {
              "intro": package.get('description'),
              "rules": f"You will be battling a {enemy.humanized_name}. You will have as much time as you need to prep before the battle, but once the battle starts you will have only seconds per move (keep an eye on the timer in the bottom right; don't run out of time!).",
              "seconds_per_question": seconds_per_question,
              'est_read_time_mins': package.get('est_read_time_mins', 20),
              "prep_materials": [
                {
                  "url": package.get('reading_material_url'),
                  "title": package.get('reading_material_name')
                }
              ]
            }
            game_metadata = {
              "video": package.get('background').replace('back', 'bg') + ".mp4" if package.get('video_enabled', 0) else None,
              "enemy": {
                "id": enemy.pk,
                "art": enemy.img_url,
                "level": "1",
                "title": enemy.humanized_name
              }
            }

            try:
                funct = Quest.objects.create
                edit_comments = ""
                visible = False
                if pk:
                    funct = Quest.objects.filter(pk=pk).update
                    edit_comments = quest.edit_comments
                    visible = quest.visible
                if package.get('comment'):
                    edit_comments += f"\n {timezone.now().strftime('%Y-%m-%dT%H:%M')}: {package['comment']} "

                quest = funct(
                    title=package.get('title'),
                    description=package.get('description'),
                    questions=questions,
                    game_schema=game_schema,
                    game_metadata=game_metadata,
                    kudos_reward=reward,
                    cooldown_minutes=package.get('minutes'),
                    background=package.get('background'),
                    visible=visible,
                    difficulty=package.get('difficulty'),
                    style=package.get('style'),
                    value=points,
                    creator=quest.creator if pk else request.user.profile,
                    edit_comments=edit_comments,
                    )
                if type(quest) == int:
                    quest = Quest.objects.get(pk=pk)
                new_quest_request(quest, is_edit=bool(pk))
                msg = f'Quest submission received.  We will respond via email in a few business days.  In the meantime, feel free to test your new quest @ {quest.url}'
                if pk:
                    msg = 'Edit has been made & administrators have been notified to re-review your quest (this is a SPAM/XSS prevention thing that we hope to eventually decentralize..).'
                messages.info(request, msg)
                if quest.is_dead_end:
                    messages.warning(request, "Warning: this quest has at least one dead end question (no possible answers). It won't be approved until that is corrected.")
            except Exception as e:
                if settings.DEBUG:
                    raise e
                logger.exception(e)
                messages.error(request, 'An unexpected error has occurred')

    #load edit page
    if pk and not package.get('title'):
        questions = quest.questions
        for key, val in quest.to_standard_dict().items():
            package[key] = val
        package['est_read_time_mins'] = quest.game_schema.get('est_read_time_mins')
        package['reading_material_url'] = quest.game_schema.get('prep_materials', [{}])[0].get('url')
        package['reading_material_name'] = quest.game_schema.get('prep_materials', [{}])[0].get('title')
        package['video_enabled'] = quest.video
        package['reward'] = quest.kudos_reward.pk if quest.kudos_reward else None
        package['enemy'] = quest.game_metadata.get('enemy', {}).get('id')
        package['points'] = quest.value
        package['minutes'] = quest.cooldown_minutes

    params = {
        'title': 'New Quest Application' if not quest else "Edit Quest",
        'pk': pk if not quest else quest.pk,
        'package': package,
        'the_quest': quest,
        'video_enabled_backgrounds': [f"back{i}" for i in video_enabled_backgrounds],
        'questions': questions,
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-05.png')),
        'backgrounds': [ele[0] for ele in Quest.BACKGROUNDS],
        'answer_correct': request.POST.getlist('answer_correct[]',[]),
        'seconds_to_respond': request.POST.getlist('seconds_to_respond[]',[]),
        'answer': request.POST.getlist('answer[]',[]),
    }
    return TemplateResponse(request, 'quests/new.html', params)


def get_package_helper(quest_qs, request):
    return [(ele.is_unlocked_for(request.user), ele.is_beaten(request.user), ele.is_within_cooldown_period(request.user), ele) for ele in quest_qs]


def index(request):

    # setup
    print(f" start at {round(time.time(),2)} ")
    query = request.GET.get('q', '')
    hours_new = 48 if not settings.DEBUG else 300
    quests = []
    selected_tab = 'Search' if query else 'Beginner'
    show_quests = request.GET.get('show_quests', False)
    show_loading = not show_quests
    focus_hackathon = request.GET.get('focus_hackathon', False)

    if show_quests:

        # hackathon tab
        if focus_hackathon:
            quest_qs = Quest.objects.filter(visible=True).filter(unlocked_by_hackathon__slug=focus_hackathon)
            quest_package = get_package_helper(quest_qs, request)
            package = ('Hackathon Quests', quest_package)
            quests.append(package)

        print(f" phase1.0 at {round(time.time(),2)} ")

        # search tab
        if query:
            quest_qs = Quest.objects.filter(visible=True).filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(questions__icontains=query) | Q(game_schema__icontains=query) | Q(game_metadata__icontains=query)).order_by('-ui_data__success_pct')
            quest_package = get_package_helper(quest_qs, request)
            package = ('Search', quest_package)
            quests.append(package)
        print(f" phase1.1 at {round(time.time(),2)} ")

        # beaten/unbeaten
        if request.user.is_authenticated:
            attempts = request.user.profile.quest_attempts
            if attempts.exists():
                beaten = Quest.objects.filter(pk__in=attempts.filter(success=True).values_list('quest', flat=True))
                unbeaten = Quest.objects.filter(pk__in=attempts.filter(success=False).exclude(quest__in=beaten).values_list('quest', flat=True))
                if unbeaten.exists():
                    quests.append(('Attempted', get_package_helper(unbeaten, request)))
                    if selected_tab != 'Search':
                        selected_tab = 'Attempted'
                if beaten.exists():
                    quests.append(('Beaten', get_package_helper(beaten, request)))
                created_quests = request.user.profile.quests_created.filter(visible=True)
                if created_quests:
                    quests.append(('Created', get_package_helper(created_quests, request)))

        print(f" phase1.2 at {round(time.time(),2)} ")
        # difficulty tab
        for diff in Quest.DIFFICULTIES:
            quest_qs = Quest.objects.filter(difficulty=diff[0], visible=True).order_by('-ui_data__success_pct')
            quest_package = get_package_helper(quest_qs, request)
            package = (diff[0], quest_package)
            if quest_qs.exists():
                quests.append(package)

        print(f" phase1.3 at {round(time.time(),2)} ")
        # new quests!
        new_quests = Quest.objects.filter(visible=True, created_on__gt=(timezone.now() - timezone.timedelta(hours=hours_new))).order_by('-ui_data__success_pct')
        if new_quests.exists():
            quests.append(('New', get_package_helper(new_quests, request)))

        print(f" phase1.4 at {round(time.time(),2)} ")
        # popular quests
        popular = Quest.objects.filter(visible=True).order_by('-ui_data__attempts_count')[0:15]
        if popular.exists():
            quests.append(('Popular', get_package_helper(popular, request)))

        # select focus
        if focus_hackathon:
            selected_tab = 'Hackathon Quests'


    print(f" phase2 at {round(time.time(),2)} ")
    rewards_schedule = []
    for i in range(0, max_ref_depth):
        reward_denominator = 2 ** i
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

    quests_attempts_per_day = (abs(round(QuestAttempt.objects.count() /
                                         (QuestAttempt.objects.first().created_on - timezone.now()).days, 1))
                               if QuestAttempt.objects.count() else 0)
    success_ratio = int(success_count / attempt_count * 100) if attempt_count else 0
    # community_created
    params = {
        'profile': request.user.profile if request.user.is_authenticated else None,
        'quests': quests,
        'avg_play_count': round(QuestAttempt.objects.count()/(Quest.objects.count() or 1), 1),
        'quests_attempts_total': QuestAttempt.objects.count(),
        'quests_total': Quest.objects.filter(visible=True).count(),
        'quests_attempts_per_day': quests_attempts_per_day,
        'total_visible_quest_count': Quest.objects.filter(visible=True).count(),
        'gitcoin_created': Quest.objects.filter(visible=True).filter(creator=Profile.objects.filter(handle='gitcoinbot').first()).count(),
        'community_created': Quest.objects.filter(visible=True).exclude(creator=Profile.objects.filter(handle='gitcoinbot').first()).count(),
        'country_count': 87,
        'email_count': EmailSubscriber.objects.count(),
        'attempt_count': attempt_count,
        'success_count': success_count,
        'success_ratio': success_ratio,
        'user_count': QuestAttempt.objects.distinct('profile').count(),
        'leaderboard': leaderboard,
        'REFER_LINK': f'https://gitcoin.co/quests/?cb=ref:{request.user.profile.ref_code}' if request.user.is_authenticated else None,
        'rewards_schedule': rewards_schedule,
        'query': query,
        'latest_round_winners': ['walidmujahid', 'nazariyv', 'cpix18'],
        'selected_tab': selected_tab,
        'title': f' {query.capitalize()} Quests',
        'point_history': point_history,
        'point_value': point_value,
        'show_loading': show_loading,
        'current_round_number': current_round_number,
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-05.png')),
        'card_desc': 'Gitcoin Quests is a fun, gamified way to learn about the web3 ecosystem, compete with your friends, earn rewards, and level up your decentralization-fu!',
    }

    print(f" phase5 at {round(time.time(),2)} ")
    return TemplateResponse(request, 'quests/index.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='1/m', method=ratelimit.UNSAFE, block=True)
def feedback(request, obj_id):
    return details(request, obj_id, '', allow_feedback=True)


@csrf_exempt
@ratelimit(key='ip', rate='10/s', method=ratelimit.UNSAFE, block=True)
def details(request, obj_id, name, allow_feedback=False):
    """Render the Quests 'detail' page."""
    # lookup quest
    if not re.match(r'\d+', obj_id):
        raise ValueError(f'Invalid obj_id found.  ID is not a number:  {obj_id}')
    try:
        quest = Quest.objects.get(pk=obj_id)
        if not quest.is_unlocked_for(request.user):
            unlock_how = f"Unlock this quest by registering for {quest.unlocked_by_hackathon.name} Hackathon" if quest.unlocked_by_hackathon else f"Unlock by beating the '{quest.self.unlocked_by_quest}' Quest"
            messages.info(request, f'This quest is locked. Try again after you have unlocked it. ({unlock_how})')
            return redirect('/quests')
    except:
        raise Http404

    # handle user feedback
    if allow_feedback and request.user.is_authenticated and request.POST.get('feedback'):
        comment = request.POST.get('feedback')
        vote = int(request.POST.get('polarity'))
        if vote not in [-1, 1]:
            vote = 0
        from quests.models import QuestFeedback
        QuestFeedback.objects.create(
            profile=request.user.profile,
            quest=quest,
            comment=comment,
            vote=vote,
            )
        if comment:
            send_user_feedback(quest, comment, request.user)
        return JsonResponse({'status': 'ok'})
    if quest.style.lower() == 'quiz':
        return quiz_style(request, quest)
    elif quest.style == 'Example for Demo':
        return example(request, quest)
    else:
        raise Exception(f'Not supported quest style: {quest.style}')
