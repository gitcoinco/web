import re

from django.conf import settings
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone

from dashboard.models import Activity, HackathonEvent, get_my_earnings_counter_profiles, get_my_grants
from kudos.models import Token
from marketing.mails import comment_email, mention_email, new_action_request
from ratelimit.decorators import ratelimit

from .models import Announcement, Comment, Flag, Like, Offer, OfferAction
from .tasks import increment_offer_view_counts
from .utils import is_user_townsquare_enabled


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
        year += 1 if month > 11 else 0
        month += 1
        d = timezone.datetime(year=year, month=month, day=1)
    return d


def index(request):

    # TODO: temporary until town square is approved for non-staff use
    if not is_user_townsquare_enabled(request.user):
        from retail.views import index as regular_homepage
        return regular_homepage(request)

    return town_square(request)

def town_square(request):

    # setup tabas
    tabs = [{
        'title': "Everywhere",
        'slug': 'everywhere',
        'helper_text': 'Activity everywhere in the Gitcoin network',
    }]
    default_tab = 'everywhere'
    if request.user.is_authenticated:
        num_business_relationships = len(set(get_my_earnings_counter_profiles(request.user.profile.pk)))
        if num_business_relationships:
            new_tab = {
                'title': f"Relationships ({num_business_relationships})",
                'slug': 'my_tribes',
                'helper_text': f'Activity from the {num_business_relationships} users who you\'ve done business with Gitcoin',
            }
            tabs = [new_tab] + tabs
            default_tab = 'my_tribes'
        num_grants_relationships = len(set(get_my_grants(request.user.profile)))
        if num_grants_relationships:
            new_tab = {
                'title': f'Grants ({num_grants_relationships})',
                'slug': f'grants',
                'helper_text': f'Activity on the {num_grants_relationships} Grants you\'ve created or funded.',
            }
            tabs = [new_tab] + tabs
            default_tab = 'grants'

    connect_last_24_hours = Activity.objects.filter(activity_type='status_update', created_on__gt=timezone.now() - timezone.timedelta(hours=24)).count()
    if connect_last_24_hours:
        default_tab = 'connect'
        connect = {
            'title': f"Connect ({connect_last_24_hours})",
            'slug': f'connect',
            'helper_text': f'The {connect_last_24_hours} announcements, requests for help, jobs, mentorship, or other connective requests on Gitcoin in the last 24 hours.',
        }
        tabs = [connect] + tabs

    if request.user.is_authenticated:
        hackathons = HackathonEvent.objects.filter(start_date__lt=timezone.now(), end_date__gt=timezone.now())
        if hackathons.count():
            user_registered_hackathon = request.user.profile.hackathon_registration.filter(registrant=request.user.profile, hackathon__in=hackathons).first()
            if user_registered_hackathon:
                default_tab = f'hackathon:{user_registered_hackathon.hackathon.pk}'
                connect = {
                    'title': user_registered_hackathon.hackathon.name,
                    'slug': default_tab,
                    'helper_text': f'Activity from the {user_registered_hackathon.hackathon.name} Hackathon.',
                }
                tabs = [connect] + tabs

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

    # get offers
    offer_pks = []
    offers_by_category = {}
    for key in ['secret', 'random', 'daily', 'weekly', 'monthly']:
        next_time_available = get_next_time_available(key)
        offer = Offer.objects.current().filter(key=key).order_by('-pk').first()
        if offer:
            offer_pks.append(offer.pk)
        if request.user.is_authenticated:
            if request.user.profile.offeractions.filter(what='click', offer=offer):
                offer = None
        offers_by_category[key] = {
            'offer': offer,
            'time': next_time_available.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
    increment_offer_view_counts.delay(offer_pks)

    # subscriber info
    is_subscribed = False
    if request.user.is_authenticated:
        email_subscriber = request.user.profile.email_subscriptions.first()
        if email_subscriber:
            is_subscribed = email_subscriber.should_send_email_type_to('new_bounty_notifications')

    # announcements
    announcements = Announcement.objects.current()

    # title
    title = 'Home'
    desc = 'View the recent activity on the Gitcoin network'
    page_seo_text_insert = ''
    avatar_url = ''
    if "activity:" in tab:
        try:
            pk = int(tab.split(':')[1])
            activity = Activity.objects.get(pk=pk)
            title = f"@{activity.profile.handle}'s comment on Gitcoin "
            desc = f"{activity.text}"
            comments_count = activity.comments.count()
            if comments_count:
                title += f"(+ {comments_count} comments)"
            avatar_url = activity.profile.avatar_url
            page_seo_text_insert = desc
        except:
            pass


    # render page context
    trending_only = int(request.GET.get('trending', 0))
    context = {
        'title': title,
        'card_desc': desc,
        'avatar_url': avatar_url,
        'page_seo_text_insert': page_seo_text_insert,
        'nav': 'home',
        'target': f'/activity?what={tab}&trending_only={trending_only}',
        'tab': tab,
        'tabs': tabs,
        'now': timezone.now(),
        'trending_only': bool(trending_only),
        'search': search,
        'tags': [('#announce','bullhorn'), ('#mentor','terminal'), ('#jobs','code'), ('#help','laptop-code'), ('#other','briefcase'), ],
        'announcements': announcements,
        'is_subscribed': is_subscribed,
        'offers_by_category': offers_by_category,
    }
    response = TemplateResponse(request, 'townsquare/index.html', context)
    if request.GET.get('tab'):
        response.set_cookie('tab', request.GET.get('tab'))
    return response


@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
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

    # check for permissions
    has_perms = request.user.is_authenticated
    if request.POST.get('method') == 'delete':
        has_perms = activity.profile == request.user.profile
    if not has_perms:
        raise Http404

    # deletion request
    if request.POST.get('method') == 'delete':
        activity.delete()

    # like request
    elif request.POST.get('method') == 'like':
        if request.POST['direction'] == 'liked':
            Like.objects.create(profile=request.user.profile, activity=activity)
        if request.POST['direction'] == 'unliked':
            activity.likes.filter(profile=request.user.profile).delete()

    # flag request
    elif request.POST.get('method') == 'flag':
        if request.POST['direction'] == 'flagged':
            Flag.objects.create(profile=request.user.profile, activity=activity)
            flag_threshold_to_hide = 3 #hides comment after 3 flags
            is_hidden_by_users = activity.flags.count() > flag_threshold_to_hide
            is_hidden_by_staff = activity.flags.filter(profile__user__is_staff=True).count() > 0
            is_hidden = is_hidden_by_users or is_hidden_by_staff
            if is_hidden:
                activity.hidden = True
                activity.save()
        if request.POST['direction'] == 'unflagged':
            activity.flags.filter(profile=request.user.profile).delete()

    # comment request
    elif request.POST.get('method') == 'comment':
        comment = request.POST.get('comment')
        comment = Comment.objects.create(profile=request.user.profile, activity=activity, comment=comment)
        to_emails = set(activity.comments.exclude(profile=request.user.profile).values_list('profile__email', flat=True))
        comment_email(comment, to_emails)

        username_pattern = re.compile(r'@(\S+)')
        mentioned_usernames = re.findall(username_pattern, title)
        mentioned_emails = set(Profile.objects.filter(handle__in=mentioned_usernames).values_list('email', flat=True))
        # Don't send emails again to users who already received a comment email
        deduped_emails = mentioned_emails.difference(to_emails)
        mention_email(comment, deduped_emails)

    elif request.GET.get('method') == 'comment':
        comments = activity.comments.order_by('created_on')
        comments = [comment.to_standard_dict(properties=['profile_handle']) for comment in comments]
        response['comments'] = comments
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
            return redirect('/login/github?next=' + request.get_full_path())
        offer = get_offer_and_create_offer_action(request.user.profile, offer_id, 'go', True)
        return redirect(offer.url)
    except:
        raise Http404


def offer_decline(request, offer_id, offer_slug):

    try:
        offer = Offer.objects.current().get(pk=offer_id)
        if not request.user.is_authenticated:
            return redirect('/login/github?next=' + request.get_full_path())
        offer = get_offer_and_create_offer_action(request.user.profile, offer_id, 'decline', True)
        return redirect('/')
    except:
        raise Http404


def offer_view(request, offer_id, offer_slug):

    try:
        offer = Offer.objects.current().get(pk=offer_id)
        if not request.user.is_authenticated:
            return redirect('/login/github?next=' + request.get_full_path())
        is_debugging_offers = request.GET.get('preview', 0)
        if request.user.profile.offeractions.filter(what='click', offer=offer) and not is_debugging_offers:
            raise Exception('already visited this offer')
        OfferAction.objects.create(profile=request.user.profile, offer=offer, what='click')
        # render page context
        context = {
            'title': offer.title,
            'card_desc': offer.desc,
            'nav': 'home',
            'offer': offer,
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
                persona=Token.objects.get(pk=package.get('persona')),
                valid_from=timezone.now(),
                valid_to=timezone.now(),
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
        'nav': 'home',
    }
    return TemplateResponse(request, 'townsquare/new.html', context)
