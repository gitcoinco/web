
import copy
import logging
import random

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Sum 
from django.shortcuts import redirect, render
from django.utils import timezone

from dashboard.models import Activity
from inbox.utils import send_notification_to_user
from kudos.models import BulkTransferCoupon, BulkTransferRedemption, Token
from kudos.views import get_profile
from perftools.models import JSONStore
from quests.models import Quest, QuestAttempt, QuestPointAward

logger = logging.getLogger(__name__)

max_ref_depth = 4

def record_quest_activity(quest, associated_profile, event_name, override_created=None):
    """
    Creates activity feeds from people doing quests.
    """

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


def record_award_helper(qa, profile, layer=1, action='Beat', value_multiplier=1):
    """
    Awards point awards (and referral rewards) to a winner
    """

    #max depth
    if layer > max_ref_depth:
        return

    # record points
    value = abs(value_multiplier * qa.quest.value/(10**(layer-1)))
    from quests.views import current_round_number
    QuestPointAward.objects.create(
        questattempt=qa,
        profile=profile,
        value=value,
        action=action,
        round_number=current_round_number,
        )

    # record kudos
    if layer > 1 or settings.DEBUG:
        gitcoinbot = get_profile('gitcoinbot')
        quest = qa.quest
        btc = BulkTransferCoupon.objects.create(
            token=quest.kudos_reward,
            tag='quest',
            num_uses_remaining=1,
            num_uses_total=1,
            current_uses=0,
            secret=random.randint(10**19, 10**20),
            comments_to_put_in_kudos_transfer=f"Congrats on beating the '{quest.title}' Gitcoin Quest",
            sender_profile=gitcoinbot,
            metadata={
                'recipient': profile.pk,
            },
            make_paid_for_first_minutes=1,
            )
        cta_url = btc.url
        cta_text = 'Redeem Kudos'
        msg_html = f"@{qa.profile.handle} just beat '{qa.quest.title}'.  You earned {round(value,2)} quest points & a kudos for referring them."
        send_notification_to_user(gitcoinbot.user, profile.user, cta_url, cta_text, msg_html)

    # recursively record points for your referals quest
    if profile.referrer:
        return record_award_helper(qa, profile.referrer, layer+1, action, value_multiplier)


def get_base_quest_view_params(user, quest):
    """
    Gets the base quest view params
    """
    profile = user.profile if user.is_authenticated else None
    attempts = quest.attempts.filter(profile=profile) if profile else QuestAttempt.objects.none()
    is_owner = quest.creator.pk == user.profile.pk if user.is_authenticated else False
    title = "Play the *" + quest.title + "* Gitcoin Quest"
    if quest.kudos_reward:
        title += f" and win a *{quest.kudos_reward.humanized_name}* Kudos"
    if quest.reward_tip:
        title = f"[WIN {quest.reward_tip.value_true} {quest.reward_tip.tokenName}] " + title
    params = {
        'quest': quest,
        'hide_col': True,
        'attempt_count': attempts.count() + 1,
        'success_count': attempts.filter(success=True).count(),
        'is_owner': is_owner,
        'is_owner_or_staff': is_owner or user.is_staff,
        'body_class': 'quest_battle',
        'title': title,
        'avatar_url': quest.avatar_url_png,
        'card_desc': quest.description,
        'seconds_per_question': quest.game_schema.get('seconds_per_question', 30),
        'quest_json': quest.to_json_dict(exclude="questions"),
        'prize_url': get_prize_url_if_redeemable(user, quest),
    }
    return params


def get_prize_url_if_redeemable(user, quest):
    """
    Gets the prize_url if redeemable (IFF quest beaten and not already redeemed)
    """
    if not quest.visible:
        return None
    if not user.is_authenticated:
        return None
    btcs = BulkTransferCoupon.objects.filter(
        token=quest.kudos_reward,
        tag='quest',
        comments_to_put_in_kudos_transfer=f"Congrats on beating the '{quest.title}' Gitcoin Quest",
        metadata__recipient=user.profile.pk,
        num_uses_remaining__gt=0,
        )
    if btcs.exists():
        return tweetify_prize_url(btcs.first().url, quest, user)
    return None


def tweetify_prize_url(url, quest, user):
    tweet_url = f"{quest.url}?cb=ref:{user.profile.ref_code}"
    prize_url = f"{url}?tweet_url={tweet_url}&tweet=I just won a {quest.kudos_reward.humanized_name} Kudos by beating the '{quest.title} Quest' on @gitcoin quests."
    return prize_url


def get_active_attempt_if_any(user, quest, state=None):
    """
    Gets the active quest attempt if any
    """
    profile = user.profile if user.is_authenticated else None
    minutes = quest.cooldown_minutes if quest.cooldown_minutes >= 1 else 3
    active_attempts = QuestAttempt.objects.filter(
        quest=quest,
        profile=profile,
        success=False,
        modified_on__gt=(timezone.now()-timezone.timedelta(minutes=minutes))
    )
    if state:
        active_attempts = active_attempts.filter(state=state)
    active_attempt = active_attempts.order_by('-pk').first()
    return active_attempt


def process_start(request, quest):
    """
    Processes the start of the quest oh behalf of the user
    """
    QuestAttempt.objects.create(
        quest=quest,
        success=False,
        profile=request.user.profile,
        state=0,
        )
    record_quest_activity(quest, request.user.profile, 'played_quest')


def get_or_create_prize_url(quest, profile):
    tweet_url = f"{settings.BASE_URL}{quest.url}".replace('gitcoin.co//', 'gitcoin.co/') #total hack but prevents https://github.com/gitcoinco/web/issues/5298#issuecomment-545657239
    reward = f"{quest.kudos_reward.humanized_name} Kudos" if quest.kudos_reward else f"{quest.reward_tip.value_true} {quest.reward_tip.tokenName}"
    add_params = f"?cb=ref:{profile.ref_code}&tweet_url={tweet_url}&tweet=I just won a {reward} by beating the '{quest.title} Quest' on @gitcoin quests."
    if quest.reward_tip:
        return f"{quest.reward_tip.receive_url}{add_params}"
    else:
        btc = None
        btcs = BulkTransferCoupon.objects.filter(
            token=quest.kudos_reward,
            tag='quest',
            metadata__recipient=profile.pk)
        if btcs.exists():
            btc = btcs.first()
        else:
            btc = BulkTransferCoupon.objects.create(
                token=quest.kudos_reward,
                tag='quest',
                num_uses_remaining=1,
                num_uses_total=1,
                current_uses=0,
                secret=random.randint(10**19, 10**20),
                comments_to_put_in_kudos_transfer=f"Congrats on beating the '{quest.title}' Gitcoin Quest",
                sender_profile=get_profile('gitcoinbot'),
                metadata={
                    'recipient': profile.pk,
                },
            )
        prize_url = f"{btc.url}{add_params}"
        return prize_url



def process_win(request, qa):
    """
    Processes the win on behalf of the user
    """

    if qa.profile.pk != request.user.profile.pk:
        messages.info(request, "Invalid Quest attempt")
        return "https://gitcoin.co/quests"
    quest = qa.quest
    was_already_beaten = quest.is_beaten(request.user)
    first_time_beaten = not was_already_beaten
    record_quest_activity(quest, request.user.profile, 'beat_quest')
    prize_url = get_or_create_prize_url(quest, request.user.profile)
    qa.success = True
    qa.save()
    if not qa.quest.visible:
        # return a mock prize URL because quiz not approved yet
        messages.info(request, "cannot redeem prize for a quest thats not live yet! returning you to quests homepage")
        return "https://gitcoin.co/quests"
    if first_time_beaten:
        record_award_helper(qa, qa.profile)
    return prize_url


def get_leaderboard(max_entries=25, round_number=1):
    try:
        return JSONStore.objects.filter(view='quests', key=f'leaderboard_{round_number}').order_by('-pk').first().data
    except:
        return {}


def generate_leaderboard(max_entries=25, round_number=1):
    """
    Gets the leaderboard that will be shown on /quests landing page
    """

    #setup
    kudos_to_show_per_leaderboard_entry = 5
    leaderboard = {}

    # groupby and sum the values (by profile)
    leaderboard = QuestPointAward.objects.filter(round_number=round_number)\
        .values('profile__handle').annotate(occ=Count('profile__handle'), sum=Sum('value'))\
        .order_by('-sum')[:max_entries]

    # add kudos to each leaderboard item
    return_leaderboard = []
    reward_kudos = {
        1: 621,
        2: 618,
        3: 622,
    }

    # assemble leaderboard
    counter = 0
    for ele in leaderboard:
        counter += 1
        btr = BulkTransferRedemption.objects.filter(coupon__tag='quest',redeemed_by__handle=ele['profile__handle']).order_by('-created_on')
        kudii = list(set([(_ele.coupon.token.img_url, _ele.coupon.token.humanized_name) for _ele in btr]))[:kudos_to_show_per_leaderboard_entry]
        display_pts = int(ele['sum']) if not ele['sum'] % 1 else round(ele['sum'],1)
        reward_kudos_pk = reward_kudos.get(counter)
        reward_kudoses = Token.objects.get(pk=reward_kudos_pk) if reward_kudos_pk else None
        reward_kudos_url = [None, None]
        if reward_kudoses:
            reward_kudos_url = [reward_kudoses.preview_img_url, reward_kudoses.humanized_name]
        this_ele = [ele['profile__handle'], display_pts, kudii, reward_kudos_url, counter]
        return_leaderboard.append(this_ele)

    # return values
    leaderboard_hero = copy.deepcopy(return_leaderboard)
    if len(leaderboard) < 3:
        leaderboard_hero = []
    else:
        leaderboard = leaderboard[3:]
        # swap locationms of 1 and 2
        tmp = None
        tmp = leaderboard_hero[0]
        leaderboard_hero[0] = leaderboard_hero[1]
        leaderboard_hero[1] = tmp
        leaderboard_hero = leaderboard_hero[:3]
        
    return return_leaderboard, leaderboard_hero
