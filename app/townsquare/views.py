import re
import time
from random import random, shuffle

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import metadata_parser
from app.services import RedisService
from dashboard.helpers import load_files_in_directory
from dashboard.models import (
    Activity, HackathonEvent, Profile, TribeMember, get_my_earnings_counter_profiles, get_my_grants,
)
from kudos.models import Token
from marketing.mails import comment_email, mention_email, new_action_request, tip_comment_awarded_email
from perftools.models import JSONStore
from ratelimit.decorators import ratelimit
from retail.views import get_specific_activities

from .models import (
    Announcement, Comment, Favorite, Flag, Like, MatchRanking, MatchRound, Offer, OfferAction, PinnedPost,
    SuggestedAction,
)
from .tasks import increment_offer_view_counts
from .utils import can_pin, is_user_townsquare_enabled

redis = RedisService().redis

tags = [
    ['#announce','bullhorn','search-announce'],
    ['#mentor','terminal','search-mentor'],
    ['#jobs','code','search-jobs'],
    ['#bounty','hand-holding-usd','search-bounty'],
    ['#help','laptop-code','search-help'],
    ['#meme','images','search-meme'],
    ['#music','music','search-music'],
    ['#other','briefcase','search-other'],
    ]


def load_wallpapers(request):
    """Load profile banners"""
    images_with_icons = load_files_in_directory('status_backgrounds')
    images = [image.split('.')[0] for image in images_with_icons if 'icon' not in image]
    response = {
        'status': 200,
        'wallpapers': images
    }
    return JsonResponse(response, safe=False)

def get_next_time_available(key):
    d = timezone.now()
    next_offer = Offer.objects.filter(key=key, valid_from__gt=d).order_by('valid_from')
    if next_offer.exists():
        return next_offer.first().valid_from
    if key == 'daily':
        hours = 24 - int(d.strftime('%H'))
        minutes = 60 - int(d.strftime('%M'))
        d = d + timezone.timedelta(hours=hours) + timezone.timedelta(minutes=minutes)
    if key == 'weekly':
        d = d + timezone.timedelta(days=5 - d.weekday())
    if key == 'monthly':
        month = int(d.strftime('%m'))
        year = int(d.strftime('%Y'))

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

        d = timezone.datetime(year=year, month=month, day=1)
    return d


def index(request):

    return town_square(request)


def max_of_ten(n):
    return "10+" if n >= 10 else n


def get_amount_unread(key, request):
    if key == request.GET.get('tab'):
        return 0
    if key == request.COOKIES.get('tab'):
        return 0
    posts_unread = 0
    post_data_cache = JSONStore.objects.filter(view='activity', key=key)
    if post_data_cache.exists():
        data = post_data_cache.first().data
        elements = []
        if isinstance(data, list):
            elements = [ele for ele in data if ele > request.session.get(key, 0)]
        posts_unread = len(elements)
    return max_of_ten(posts_unread)


def get_sidebar_tabs(request):
    # setup tabs
    hours = 24
    hackathon_tabs = []
    tabs = [{
        'title': f"Everywhere",
        'slug': 'everywhere',
        'helper_text': f'The activity feed items everywhere in the Gitcoin network',
        'badge': get_amount_unread('everywhere', request),
    }]
    default_tab = 'everywhere'
    if request.user.is_authenticated:
        num_business_relationships = len(set(get_my_earnings_counter_profiles(request.user.profile.pk)))
        if num_business_relationships:
            key = 'my_tribes'
            new_tab = {
                'title': f"Relationships",
                'slug': key,
                'helper_text': f'Activity from the users who you\'ve done business with Gitcoin',
                'badge': 0
            }
            tabs = [new_tab] + tabs
            default_tab = 'my_tribes'

        num_grants_relationships = (len(set(get_my_grants(request.user.profile))))
        if num_grants_relationships:
            key = 'grants'
            new_tab = {
                'title': f'Grants',
                'slug': key,
                'helper_text': f'Activity on the Grants you\'ve created or funded.',
                'badge': 0,
            }
            tabs = [new_tab] + tabs
            default_tab = 'grants'

        num_favorites = request.user.favorites.filter(grant=None).all().count()
        if num_favorites:
            key = 'my_favorites'
            activities = 0
            new_tab = {
                'title': f"My Favorites",
                'slug': key,
                'helper_text': f'Activity that you marked as favorite',
                'badge': max_of_ten(activities) if request.GET.get(
                    'tab') != key else 0
            }
            tabs = [new_tab] + tabs
            default_tab = 'my_favorites'

        threads_last_24_hours = max_of_ten(request.user.profile.subscribed_threads.filter(pk__gt=request.session.get('my_threads', 0)).count())  if request.GET.get('tab') != 'my_threads' else 0

        threads = {
            'title': f"My Threads",
            'slug': f'my_threads',
            'helper_text': f'The Threads that you\'ve liked, commented on, or sent a tip upon on Gitcoin since you last checked.',
            'badge': threads_last_24_hours
        }
        tabs = [threads] + tabs

    default_tab = 'connect'
    connect = {
        'title': f"Connect",
        'slug': f'connect',
        'helper_text': f'The announcements, requests for help, kudos jobs, mentorship, or other connective requests on Gitcoin.',
        'badge': get_amount_unread('connect', request),
    }
    tabs = [connect] + tabs

    connect = {
        'title': f"Kudos",
        'slug': f'kudos',
        'helper_text': f'The Kudos that have been sent by Gitcoin community members, to show appreciation for one aother.',
        'badge': get_amount_unread('kudos', request),
    }
    tabs = tabs + [connect]

    start_date = timezone.now() + timezone.timedelta(days=28)
    end_date = timezone.now() - timezone.timedelta(days=7)
    hackathons = HackathonEvent.objects.filter(start_date__lt=start_date, end_date__gt=end_date, visible=True)
    if hackathons.count():
        for hackathon in hackathons:
            connect = {
                'title': hackathon.name,
                'logo': hackathon.logo,
                'start': hackathon.start_date,
                'end': hackathon.end_date,
                'slug': f'hackathon:{hackathon.pk}',
                'url_slug': hackathon.slug,
                'helper_text': f'Go to {hackathon.name} Townsquare.',
            }
            hackathon_tabs = [connect] + hackathon_tabs


    # set tab
    if request.COOKIES.get('tab'):
        all_tabs = [tab.get('slug') for tab in tabs]
        if request.COOKIES.get('tab') in all_tabs:
            default_tab = request.COOKIES.get('tab')
    tab = request.GET.get('tab', default_tab)

    is_search = "activity:" in tab or "search-" in tab
    if is_search:
        tabs.append({
            'title': "Search",
            'slug': tab,
        })
    search = ''
    if "search-" in tab:
        search = tab.split('-')[1]

    return tabs, tab, is_search, search, hackathon_tabs

def get_offers(request):
    # get offers
    offer_pks = []
    offers_by_category = {}
    available_offers = Offer.objects.current()

    if request.user.is_authenticated:
        available_offers = available_offers.exclude(actions__profile=request.user.profile, actions__what__in=['click', 'decline', 'go'])
    for key in ['top', 'secret', 'random', 'weekly', 'monthly']:
        next_time_available = get_next_time_available(key)
        offers = available_offers.filter(key=key).order_by('-pk')
        offer = offers.first()
        for offer in offers:
            offer_pks.append(offer.pk)
        offers_by_category[key] = {
            'offer': offer,
            'offers': offers,
            'time': next_time_available,
        }
    increment_offer_view_counts.delay(offer_pks)
    return offers_by_category

def get_miniclr_info(request):
    # matching leaderboard
    current_match_round = MatchRound.objects.current().first()
    if request.GET.get('round'):
        current_match_round = MatchRound.objects.get(number=request.GET.get('round'))
    num_to_show = 10
    current_match_rankings = MatchRanking.objects.filter(round=current_match_round, number__lt=(num_to_show+1)).order_by('number')
    matching_leaderboard = [
        {
            'i': obj.number,
            'following': request.user.profile == obj.profile or request.user.profile.follower.filter(org=obj.profile) if request.user.is_authenticated else False,
            'handle': obj.profile.handle,
            'contributions': obj.contributions,
            'default_match_estimate': obj.default_match_estimate,
            'match_curve': obj.sorted_match_curve,
            'contributors': obj.contributors,
            'amount': f"{int(obj.contributions_total/1000)}k" if obj.contributions_total > 1000 else round(obj.contributions_total, 2),
            'match_amount': obj.match_total,
            'you': obj.profile.pk == request.user.profile.pk if request.user.is_authenticated else False,
        } for obj in current_match_rankings[0:num_to_show]
    ]

    return matching_leaderboard, current_match_round

def get_subscription_info(request):
    # subscriber info
    is_subscribed = False
    if request.user.is_authenticated:
        email_subscriber = request.user.profile.email_subscriptions.first()
        if email_subscriber:
            is_subscribed = email_subscriber.should_send_email_type_to('new_bounty_notifications')
    return is_subscribed

def get_tags(request):

    # pull tag amounts
    view_tags = tags.copy()
    for i in range(0, len(view_tags)):
        keyword = view_tags[i][2]
        view_tags[i] = view_tags[i] + [get_amount_unread(keyword, request)]

    return view_tags

def get_param_metadata(request, tab):

    # title
    title = 'Town Square'
    desc = 'Learn, earn, & connect with great developers on the Gitcoin Town Square'
    page_seo_text_insert = ''
    avatar_url = ''
    admin_link = ''
    is_direct_link = "activity:" in tab
    if is_direct_link:
        try:
            pk = int(tab.split(':')[1])
            activity = Activity.objects.get(pk=pk)
            title = f"@{activity.profile.handle}'s post on Gitcoin "
            desc = f"{activity.text}"
            comments_count = activity.comments.count()
            admin_link = activity.admin_url
            if comments_count:
                title += f"(+ {comments_count} comments)"
            avatar_url = activity.profile.avatar_url
            page_seo_text_insert = desc
        except Exception as e:
            print(e)
    return title, desc, page_seo_text_insert, avatar_url, is_direct_link, admin_link


@login_required
@require_http_methods(['PUT'])
@csrf_exempt
def ignored_suggested_tribe(request, tribeId):
    profile = request.user.profile
    tribe_profile = get_object_or_404(Profile, handle__iexact=tribeId)

    profile.ignore_tribes.add(tribe_profile)

    return JsonResponse({
       'tribes': get_suggested_tribes(request)
    })


def get_suggested_tribes(request):
    following_tribes = []
    tribe_limit = 5

    if request.user.is_authenticated:
        profile = request.user.profile
        ignore = list(profile.ignore_tribes.all().values_list('pk', flat=True))
        ignore += list(TribeMember.objects.filter(profile=profile).distinct('org').values_list('org__pk', flat=True))
        tribes = Profile.objects.filter(is_org=True).order_by('-follower_count')
        count = tribes.count()
        ignore_count = len(ignore)

        if count > tribe_limit:
            tribes = tribes.filter(follower_count__gt=10).order_by('?')
        if len(ignore):
            tribes = tribes.exclude(pk__in=ignore).order_by('?')

        tribes = list(tribes)

        for profile in tribes:
            if len(following_tribes) > tribe_limit:
                break
            handle = profile.handle
            last_24_hours_activity = 0  # TODO: integrate this with get_amount_unread
            tribe = {
                'title': handle,
                'slug': f"tribe:{handle}",
                'helper_text': f'Activities from @{handle} since you last checked',
                'badge': last_24_hours_activity,
                'avatar_url': f'/dynamic/avatar/{handle}',
                'follower_count': profile.tribe_members.all().count()
            }
            following_tribes = following_tribes + [tribe]
    return following_tribes


def get_following_tribes(request):
    following_tribes = []
    if request.user.is_authenticated:
        handles = request.user.profile.tribe_members.filter(org__is_org=True).values_list('org__handle', flat=True)
        for handle in handles:
            last_24_hours_activity = 0 # TODO: integrate this with get_amount_unread
            tribe = {
                'title': handle,
                'slug': f"tribe:{handle}",
                'helper_text': f'Activities from @{handle} since you last checked',
                'badge': last_24_hours_activity,
                'avatar_url': f'/dynamic/avatar/{handle}'
            }
            following_tribes = [tribe] + following_tribes
    return following_tribes


def town_square(request):
    try:
        audience = redis.get(f"townsquare:audience")
        audience = str(audience.decode('utf-8')) if audience else '84244'
    except KeyError:
        data_results = JSONStore.objects.filter(view='results', key=None).first()
        if data_results:
            audience = data_results.data['audience']
            redis.set('townsquare:audience', audience)

    SHOW_DRESSING = request.GET.get('dressing', False)
    tab = request.GET.get('tab', request.COOKIES.get('tab', 'connect'))
    try:
        pinned = PinnedPost.objects.get(what=tab)
        if settings.ENV == 'prod' and pinned.activity.bounty and pinned.activity.bounty != 'mainnet':
            pinned = None
    except PinnedPost.DoesNotExist:
        pinned = None
    title, desc, page_seo_text_insert, avatar_url, is_direct_link, admin_link = get_param_metadata(request, tab)
    if not SHOW_DRESSING:
        is_search = "activity:" in tab or "search-" in tab
        trending_only = int(request.GET.get('trending', 0))
        context = {
            'title': title,
            'card_desc': desc,
            'avatar_url': avatar_url,
            'use_pic_card': True,
            'is_search': is_search,
            'is_direct_link': is_direct_link,
            'page_seo_text_insert': page_seo_text_insert,
            'nav': 'home',
            'what': tab,
            'can_pin': can_pin(request, tab),
            'pinned': pinned,
            'target': f'/activity?what={tab}&trending_only={trending_only}',
            'tab': tab,
            'tags': tags,
            'admin_link': admin_link,
            'now': timezone.now(),
            'is_townsquare': True,
            'trending_only': bool(trending_only),
            'audience': audience
        }

        return TemplateResponse(request, 'townsquare/index.html', context)

    tabs, tab, is_search, search, hackathon_tabs = get_sidebar_tabs(request)
    offers_by_category = get_offers(request)
    matching_leaderboard, current_match_round = get_miniclr_info(request)
    is_subscribed = get_subscription_info(request)
    announcements = Announcement.objects.current().filter(key='townsquare')
    view_tags = get_tags(request)
    following_tribes = get_following_tribes(request)
    suggested_tribes = get_suggested_tribes(request)

    # render page context
    trending_only = int(request.GET.get('trending', 0))
    context = {
        'title': title,
        'card_desc': desc,
        'avatar_url': avatar_url,
        'use_pic_card': True,
        'is_search': is_search,
        'is_direct_link': is_direct_link,
        'page_seo_text_insert': page_seo_text_insert,
        'nav': 'home',
        'target': f'/activity?what={tab}&trending_only={trending_only}',
        'tab': tab,
        'what': tab,
        'can_pin': can_pin(request, tab),
        'tabs': tabs,
        'pinned': pinned,
        'SHOW_DRESSING': SHOW_DRESSING,
        'hackathon_tabs': hackathon_tabs,
        'REFER_LINK': f'https://gitcoin.co/townsquare/?cb=ref:{request.user.profile.ref_code}' if request.user.is_authenticated else None,
        'matching_leaderboard': matching_leaderboard,
        'current_match_round': current_match_round,
        'admin_link': admin_link,
        'now': timezone.now(),
        'is_townsquare': True,
        'trending_only': bool(trending_only),
        'search': search,
        'tags': view_tags,
        'suggested_actions': SuggestedAction.objects.filter(active=True).order_by('-rank'),
        'announcements': announcements,
        'is_subscribed': is_subscribed,
        'offers_by_category': offers_by_category,
        'TOKENS': request.user.profile.token_approvals.all() if request.user.is_authenticated else [],
        'following_tribes': following_tribes,
        'suggested_tribes': suggested_tribes,
        'audience': audience
    }

    if 'tribe:' in tab:
        key = tab.split(':')[1]
        profile = Profile.objects.get(handle=key.lower())
        if profile.is_org:
            context['tribe'] = profile

    response = TemplateResponse(request, 'townsquare/index.html', context)
    if request.GET.get('tab'):
        if ":" not in request.GET.get('tab'):
            response.set_cookie('tab', request.GET.get('tab'))
    return response


@ratelimit(key='ip', rate='30/m', method=ratelimit.UNSAFE, block=True)
def emailsettings(request):

    if not request.user.is_authenticated:
        raise Http404

    is_subscribed = False
    if request.user.is_authenticated:
        email_subscriber = request.user.profile.email_subscriptions.first()
        if email_subscriber:
            is_subscribed = email_subscriber.should_send_email_type_to('new_bounty_notifications')

            for key in request.POST.keys():
                email_subscriber.set_should_send_email_type_to(key, bool(request.POST.get(key) == 'true'))
                email_subscriber.save()

    response = {}
    return JsonResponse(response)


@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def api(request, activity_id):

    # pull back the obj
    try:
        activity = Activity.objects.get(pk=activity_id)
    except:
        raise Http404

    # setup response
    response = {}
    status = 200

    # no perms needed responses go here
    if request.GET.get('method') == 'comment':
        comments = activity.comments.prefetch_related('profile').order_by('created_on')
        # check for permissions
        is_authenticated = request.user.is_authenticated
        if request.POST.get('method') == 'delete':
            has_perms = activity.profile == request.user.profile
        if is_authenticated:
            profile = request.user.profile

        response['comments'] = []
        results = {i : 0 for i in range(0, 15)}
        for comment in comments:
            counter = 0; start_time = time.time()
            comment_dict = comment.to_standard_dict(properties=['profile_handle'])
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['handle'] = comment.profile.handle
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            # perf - 0.3s on a 150 comment thread
            comment_dict['tip_count_eth'] = comment.tip_count_eth
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['is_liked'] = request.user.is_authenticated and (request.user.profile.pk in comment.likes)
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['like_count'] = len(comment.likes)
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['likes'] = ", ".join(comment.likes_handles) if len(comment.likes) else "no one. Want to be the first?"
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['name'] = comment.profile.data.get('name', None) or comment.profile.handle
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            # perf - 0.2 on a 150 comment thread
            comment_dict['default_match_round'] = comment.profile.matchranking_this_round.default_match_estimate if comment.profile.matchranking_this_round else None
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['match_this_round'] = comment.profile.match_this_round
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            comment_dict['sorted_match_curve'] = comment.profile.matchranking_this_round.sorted_match_curve if comment.profile.matchranking_this_round else None
            counter += 1; results[counter] += time.time() - start_time; start_time = time.time()
            if comment.is_edited:
                comment_dict['is_edited'] = comment.is_edited

            comment_dict['redeem_link'] = comment.redeem_link if is_authenticated and comment.tip and comment.tip.recipient_profile_id == profile.id else ''
            comment_dict['tip'] = bool(comment.tip)
            response['comments'].append(comment_dict)

        response['has_tip'] = False
        if activity.tip:
            user_can_redeem = request.user.profile.id == activity.tip.recipient_profile_id
            response['has_tip'] = True
            response['tip_available'] = not activity.tip.recipient_profile
            response['can_redeem'] = activity.tip.status == 'PENDING' and user_can_redeem
        response['author'] = activity.profile.handle

        for key, val in results.items():
            if settings.DEBUG:
                print(key, round(val, 2))
        return JsonResponse(response)

    # deletion request
    if request.POST.get('method') == 'delete':
        has_perms = False
        if request.user.is_authenticated:
            if activity.profile and request.user.profile.pk == activity.profile.pk:
                has_perms = True
            if activity.other_profile and request.user.other_profile.pk == activity.other_profile.pk:
                has_perms = True
        if has_perms:
            activity.delete()

    # deletion request
    if request.POST.get('method') == 'vote':
        vote = int(request.POST.get('vote'))
        index = vote
        if not activity.has_voted(request.user):
            activity.metadata['poll_choices'][index]['answers'].append(request.user.profile.pk)
            activity.save()

    # toggle like comment
    if request.POST.get('method') == 'toggle_like_comment':
        comment = activity.comments.filter(pk=request.POST.get('comment'))
        if comment.exists() and request.user.is_authenticated:
            comment = comment.first()
            profile_pk = request.user.profile.pk
            already_likes = profile_pk in comment.likes
            if not already_likes:
                comment.likes.append(profile_pk)
            else:
                comment.likes = [ele for ele in comment.likes if ele != profile_pk]
            comment.save()

    # like request
    elif request.POST.get('method') == 'like':
        if request.POST['direction'] == 'liked':
            already_likes = request.user.profile.likes.filter(activity=activity).exists()
            if not already_likes:
                Like.objects.create(profile=request.user.profile, activity=activity)
        if request.POST['direction'] == 'unliked':
            activity.likes.filter(profile=request.user.profile).delete()

    # award request
    elif request.POST.get('method') == 'award':
        comment = get_object_or_404(Comment, id=int(request.POST['comment']))
        if request.user.profile.id == activity.profile.id and comment.activity_id == activity.id:
            recipient_profile = comment.profile
            activity.tip.username = recipient_profile.username
            activity.tip.recipient_profile = recipient_profile
            activity.tip.save()
            comment.tip = activity.tip
            comment.save()
            tip_comment_awarded_email(comment, [recipient_profile.email])

    # favorite request
    elif request.POST.get('method') == 'favorite':
        if request.POST['direction'] == 'favorite':
            already_likes = Favorite.objects.filter(activity=activity, user=request.user).exists()
            if not already_likes:
                Favorite.objects.create(user=request.user, activity=activity)
        elif request.POST['direction'] == 'unfavorite':
            Favorite.objects.filter(user=request.user, activity=activity).delete()

    # PinnedPost request
    elif request.POST.get('method') == 'pin':
        what = request.POST.get('what')
        permission = can_pin(request, what)
        # handle permissions for pinning/unpinning
        if permission:
            if request.POST.get('direction') == 'pin':
                pinned_post, created = PinnedPost.objects.update_or_create(
                    what=what, defaults={"activity": activity, "user": request.user.profile}
                )
            elif request.POST.get('direction') == 'unpin':
                PinnedPost.objects.filter(what=what).delete()
        else:
            status = 401
            response['message'] = "UNAUTHORIZED"

    # flag request
    elif request.POST.get('method') == 'flag':
        if request.POST['direction'] == 'flagged':
            Flag.objects.create(profile=request.user.profile, activity=activity)
            flag_threshold_to_hide = 3 #hides comment after 3 flags
            is_hidden_by_users = activity.flags.count() > flag_threshold_to_hide
            is_hidden_by_staff = activity.flags.filter(profile__user__is_staff=True).count() > 0
            is_hidden_by_moderators = activity.flags.filter(profile__user__groups__name='Moderators').count() > 0
            is_hidden = is_hidden_by_users or is_hidden_by_staff or is_hidden_by_moderators
            if is_hidden:
                activity.hidden = True
                activity.save()
        if request.POST['direction'] == 'unflagged':
            activity.flags.filter(profile=request.user.profile).delete()

    # comment request
    elif request.POST.get('method') == 'comment':
        comment = request.POST.get('comment')
        title = request.POST.get('comment')
        if 'Just sent a tip of' not in comment:
            if not request.user.profile.is_blocked:
                comment = Comment.objects.create(profile=request.user.profile, activity=activity, comment=comment)

    return JsonResponse(response, status=status)


@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def comment_v1(request, comment_id):
    response = {
        'status': 400,
        'message': 'error: Bad Request.'
    }

    if not comment_id:
        return JsonResponse(response)

    user = request.user if request.user.is_authenticated else None

    if not user:
        response['message'] = 'user needs to be authenticated to take action'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    if not profile:
        response['message'] = 'no matching profile found'
        return JsonResponse(response)

    try:
        comment = Comment.objects.get(pk=comment_id)
    except:
        response = {
            'status': 404,
            'message': 'unable to find comment'
        }
        return JsonResponse(response)

    if comment.profile != profile:
        response = {
            'status': 401,
            'message': 'user not authorized'
        }
        return JsonResponse(response)

    method = request.POST.get('method')

    if method == 'DELETE':
        comment.delete()
        response = {
            'status': 204,
            'message': 'comment successfully deleted'
        }
        return JsonResponse(response)

    if method == 'EDIT':
        content = request.POST.get('comment')
        title = request.POST.get('comment')

        comment.comment = content
        comment.is_edited = True
        comment.save()
        response = {
            'status': 203,
            'message': 'comment successfully updated'
        }
        return JsonResponse(response)

    # no perms needed responses go here
    if request.GET.get('method') == 'GET_COMMENT':
        response = {
            'status': 202,
            'message': 'comment successfully retrieved',
            'comment': comment.comment,
        }
        return JsonResponse(response)

    return JsonResponse(response)


def get_offer_and_create_offer_action(profile, offer_id, what, do_not_allow_more_than_one_offeraction=False):
    offer = Offer.objects.current().get(pk=offer_id)
    if do_not_allow_more_than_one_offeraction and profile.offeractions.filter(what=what, offer=offer):
        raise Exception('already visited this offer')
    OfferAction.objects.create(profile=profile, offer=offer, what=what)
    return offer


def offer_go(request, offer_id, offer_slug):

    try:
        if not request.user.is_authenticated:
            return redirect('/login/github/?next=' + request.get_full_path())
        offer = get_offer_and_create_offer_action(request.user.profile, offer_id, 'go', False)
        return redirect(offer.url)
    except:
        raise Http404


def offer_decline(request, offer_id, offer_slug):

    try:
        offer = Offer.objects.current().get(pk=offer_id)
        if not request.user.is_authenticated:
            return redirect('/login/github/?next=' + request.get_full_path())
        offer = get_offer_and_create_offer_action(request.user.profile, offer_id, 'decline', False)
        return redirect('/')
    except:
        raise Http404


def offer_view(request, offer_id, offer_slug):

    try:
        is_debugging_offers = request.GET.get('preview', 0) and request.user.is_staff
        offers = Offer.objects.all()
        if not is_debugging_offers:
            offers = offers.current()
        offer = offers.get(pk=offer_id)
        if not request.user.is_authenticated:
            return redirect('/login/github/?next=' + request.get_full_path())
        if request.user.profile.offeractions.filter(what='go', offer=offer) and not is_debugging_offers:
            raise Exception('already visited this offer')
        if not is_debugging_offers:
            OfferAction.objects.create(profile=request.user.profile, offer=offer, what='click')
        # render page context
        context = {
            'title': offer.title,
            'card_desc': offer.desc,
            'nav': 'home',
            'offer': offer,
            'active': f'offer_view gitcoin-background {offer.style}',
        }
        return TemplateResponse(request, 'townsquare/offer.html', context)
    except:
        raise Http404


def offer_new(request):

    package = request.POST

    if package:
        try:
            offer = Offer.objects.create(
                title=package.get('title'),
                desc=package.get('description'),
                url=package.get('action_url'),
                from_name=package.get('from_name'),
                from_link=package.get('from_link'),
                persona=Token.objects.get(pk=package.get('persona')),
                valid_from=timezone.now(),
                valid_to=timezone.now(),
                style=package.get('background'),
                public=False,
                created_by=request.user.profile,
                )
            offer = new_action_request(offer)
            msg = "Action Submitted | Team Gitcoin will be in touch if it's a fit."
            messages.info(request, msg)
        except Exception as e:
            messages.error(request, e)

    context = {
        'title': "New Action",
        'card_desc': "Create an Action for Devs on Gitcoin - Its FREE!",
        'package': package,
        'backgrounds': [ele[0] for ele in Offer.STYLES],
        'nav': 'home',
    }
    return TemplateResponse(request, 'townsquare/new.html', context)


@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def video_presence(request):
    """Sets user presence on mattermost."""
    if not request.user.is_authenticated:
        return Http404

    roomname = request.POST.get('roomname', '').replace('meet', '')
    participants = request.POST.get('participants', '')
    activity = Activity.objects.filter(pk=roomname).first()
    set_status = activity and int(participants) >= 0

    # if so, make it so
    if set_status:
        redis = RedisService().redis
        seconds = 100 if not settings.DEBUG else 9999999
        redis.setex(roomname, seconds, participants)
    return JsonResponse({'status': 'OK'})


@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def extract_metadata_page(request):
    url = request.GET.get('url')

    if url:
        page = metadata_parser.MetadataParser(url=url, support_malformed=True, search_head_only=True, url_headers={
            'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        })
        meta = page.parsed_result.metadata
        return JsonResponse({
            'og': meta['og'],
            'twitter': meta['twitter'],
            'meta': meta['meta'],
            'dc': meta['dc'],
            'title': None if not page.get_metadatas('title') else page.get_metadatas('title', strategy=['meta', 'page', 'og', 'dc',])[0],
            'image': page.get_metadata_link('image'),
            'description': page.get_metadatas('description')[0],
            'link': page.get_discrete_url()
        })

    return JsonResponse({
        'status': 'error',
        'message': 'no url was provided'
    }, status=404)
