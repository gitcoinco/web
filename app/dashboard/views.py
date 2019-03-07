# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Gitcoin Core

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

'''
from __future__ import print_function, unicode_literals

import json
import logging
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from app.utils import clean_str, ellipses
from avatar.utils import get_avatar_context_for_user
from dashboard.utils import ProfileHiddenException, ProfileNotFoundException, get_bounty_from_invite_url, profile_helper
from economy.utils import convert_token_to_usdt
from eth_utils import to_checksum_address, to_normalized_address
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from git.utils import get_auth_url, get_github_user_data, is_github_token_valid, search_users
from kudos.models import KudosTransfer, Token, Wallet
from kudos.utils import humanize_name
from marketing.mails import admin_contact_funder, bounty_uninterested
from marketing.mails import funder_payout_reminder as funder_payout_reminder_mail
from marketing.mails import new_reserved_issue, start_work_approved, start_work_new_applicant, start_work_rejected
from marketing.models import Keyword
from pytz import UTC
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import HTTPProvider, Web3

from .helpers import get_bounty_data_for_activity, handle_bounty_views
from .models import (
    Activity, Bounty, BountyFulfillment, CoinRedemption, CoinRedemptionRequest, FeedbackEntry, Interest, LabsResearch,
    Profile, ProfileSerializer, Subscription, Tool, ToolVote, UserAction,
)
from .notifications import (
    maybe_market_tip_to_email, maybe_market_tip_to_github, maybe_market_tip_to_slack, maybe_market_to_email,
    maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter, maybe_market_to_user_discord,
    maybe_market_to_user_slack,
)
from .utils import (
    get_bounty, get_bounty_id, get_context, get_web3, has_tx_mined, record_user_action_on_interest, web3_process_bounty,
)

logger = logging.getLogger(__name__)

confirm_time_minutes_target = 4

# web3.py instance
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))


def record_user_action(user, event_name, instance):
    instance_class = instance.__class__.__name__.lower()
    kwargs = {
        'action': event_name,
        'metadata': {f'{instance_class}_pk': instance.pk},
    }

    if isinstance(user, User):
        kwargs['user'] = user
    elif isinstance(user, str):
        try:
            user = User.objects.get(username=user)
            kwargs['user'] = user
        except User.DoesNotExist:
            return

    if hasattr(user, 'profile'):
        kwargs['profile'] = user.profile

    try:
        UserAction.objects.create(**kwargs)
    except Exception as e:
        # TODO: sync_profile?
        logger.error(f"error in record_action: {e} - {event_name} - {instance}")


def record_bounty_activity(bounty, user, event_name, interest=None):
    """Creates Activity object.

    Args:
        bounty (dashboard.models.Bounty): Bounty
        user (string): User name
        event_name (string): Event name
        interest (dashboard.models.Interest): Interest

    Raises:
        None

    Returns:
        None
    """
    kwargs = {
        'activity_type': event_name,
        'bounty': bounty,
        'metadata': get_bounty_data_for_activity(bounty)
    }
    if isinstance(user, str):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return

    if hasattr(user, 'profile'):
        kwargs['profile'] = user.profile
    else:
        return

    if event_name == 'worker_applied':
        kwargs['metadata']['approve_worker_url'] = bounty.approve_worker_url(user.profile)
        kwargs['metadata']['reject_worker_url'] = bounty.reject_worker_url(user.profile)
    if event_name in ['worker_approved', 'worker_rejected'] and interest:
        kwargs['metadata']['worker_handle'] = interest.profile.handle

    try:
        return Activity.objects.create(**kwargs)
    except Exception as e:
        logger.error(f"error in record_bounty_activity: {e} - {event_name} - {bounty} - {user}")


def helper_handle_access_token(request, access_token):
    # https://gist.github.com/owocki/614a18fbfec7a5ed87c97d37de70b110
    # interest API via token
    github_user_data = get_github_user_data(access_token)
    request.session['handle'] = github_user_data['login']
    profile = Profile.objects.filter(handle__iexact=request.session['handle']).first()
    request.session['profile_id'] = profile.pk


def create_new_interest_helper(bounty, user, issue_message):
    approval_required = bounty.permission_type == 'approval'
    acceptance_date = timezone.now() if not approval_required else None
    profile_id = user.profile.pk
    record_bounty_activity(bounty, user, 'start_work' if not approval_required else 'worker_applied')
    interest = Interest.objects.create(
        profile_id=profile_id,
        issue_message=issue_message,
        pending=approval_required,
        acceptance_date=acceptance_date,
    )
    bounty.interested.add(interest)
    record_user_action(user, 'start_work', interest)
    maybe_market_to_slack(bounty, 'start_work' if not approval_required else 'worker_applied')
    maybe_market_to_user_slack(bounty, 'start_work' if not approval_required else 'worker_applied')
    maybe_market_to_user_discord(bounty, 'start_work' if not approval_required else 'worker_applied')
    maybe_market_to_twitter(bounty, 'start_work' if not approval_required else 'worker_applied')
    return interest


@csrf_exempt
def gh_login(request):
    """Attempt to redirect the user to Github for authentication."""
    return redirect('social:begin', backend='github')


def get_interest_modal(request):
    bounty_id = request.GET.get('pk')
    if not bounty_id:
        raise Http404

    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        raise Http404

    context = {
        'bounty': bounty,
        'active': 'get_interest_modal',
        'title': _('Add Interest'),
        'user_logged_in': request.user.is_authenticated,
        'login_link': '/login/github?next=' + request.GET.get('redirect', '/')
    }
    return TemplateResponse(request, 'addinterest.html', context)


@csrf_exempt
@require_POST
def new_interest(request, bounty_id):
    """Claim Work for a Bounty.

    :request method: POST

    Args:
        bounty_id (int): ID of the Bounty.

    Returns:
        dict: The success key with a boolean value and accompanying error.

    """
    profile_id = request.user.profile.pk if request.user.is_authenticated and hasattr(request.user, 'profile') else None

    access_token = request.GET.get('token')
    if access_token:
        helper_handle_access_token(request, access_token)
        github_user_data = get_github_user_data(access_token)
        profile = Profile.objects.prefetch_related('bounty_set') \
            .filter(handle=github_user_data['login']).first()
        profile_id = profile.pk
    else:
        profile = request.user.profile if profile_id else None

    if not profile_id:
        return JsonResponse(
            {'error': _('You must be authenticated via github to use this feature!')},
            status=401)

    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        raise Http404

    if bounty.is_project_type_fulfilled:
        return JsonResponse({
            'error': _(f'There is already someone working on this bounty.'),
            'success': False},
            status=401)

    num_issues = profile.max_num_issues_start_work
    active_bounties = Bounty.objects.current().filter(idx_status__in=['open', 'started'])
    num_active = Interest.objects.filter(profile_id=profile_id, bounty__in=active_bounties).count()
    is_working_on_too_much_stuff = num_active >= num_issues
    if is_working_on_too_much_stuff:
        return JsonResponse({
            'error': _(f'You may only work on max of {num_issues} issues at once.'),
            'success': False},
            status=401)

    if profile.no_times_slashed_by_staff():
        return JsonResponse({
            'error': _('Because a staff member has had to remove you from a bounty in the past, you are unable to start'
                       'more work at this time. Please leave a message on slack if you feel this message is in error.'),
            'success': False},
            status=401)

    try:
        Interest.objects.get(profile_id=profile_id, bounty=bounty)
        return JsonResponse({
            'error': _('You have already started work on this bounty!'),
            'success': False},
            status=401)
    except Interest.DoesNotExist:
        issue_message = request.POST.get("issue_message")
        interest = create_new_interest_helper(bounty, request.user, issue_message)
        if interest.pending:
            start_work_new_applicant(interest, bounty)

    except Interest.MultipleObjectsReturned:
        bounty_ids = bounty.interested \
            .filter(profile_id=profile_id) \
            .values_list('id', flat=True) \
            .order_by('-created')[1:]

        Interest.objects.filter(pk__in=list(bounty_ids)).delete()

        return JsonResponse({
            'error': _('You have already started work on this bounty!'),
            'success': False},
            status=401)

    msg = _("You have started work.")
    approval_required = bounty.permission_type == 'approval'
    if approval_required:
        msg = _("You have applied to start work.  If approved, you will be notified via email.")

    return JsonResponse({
        'success': True,
        'profile': ProfileSerializer(interest.profile).data,
        'msg': msg,
    })


@csrf_exempt
@require_POST
def post_comment(request):
    profile_id = request.user.profile if request.user.is_authenticated and hasattr(request.user, 'profile') else None
    if profile_id is None:
        return JsonResponse({
            'success': False,
            'msg': '',
        })

    sbid = request.POST.get('standard_bounties_id')
    bountyObj = Bounty.objects.filter(standard_bounties_id=sbid).first()
    fbAmount = FeedbackEntry.objects.filter(sender_profile=profile_id, feedbackType=request.POST.get('review[reviewType]', 'approver'), bounty=bountyObj).count()
    if fbAmount > 0:
        return JsonResponse({
            'success': False,
            'msg': 'There is already a approval comment',
        })
    if request.POST.get('review[reviewType]','approver') == 'approver':
        receiver_profile = Profile.objects.filter(handle=request.POST.get('review[receiver]', '')).first()
    else:
        receiver_profile = bountyObj.bounty_owner_profile
    kwargs = {
        'bounty': bountyObj,
        'sender_profile': profile_id,
        'receiver_profile': receiver_profile,
        'rating': request.POST.get('review[rating]', '-1'),
        'comment': request.POST.get('review[comment]', 'No comment.'),
        'feedbackType': request.POST.get('review[reviewType]','approver')
    }

    feedback = FeedbackEntry.objects.create(**kwargs)
    feedback.save()
    return JsonResponse({
            'success': False,
            'msg': 'Finished.'
        })


@csrf_exempt
@require_POST
def remove_interest(request, bounty_id):
    """Unclaim work from the Bounty.

    Can only be called by someone who has started work

    :request method: POST

    post_id (int): ID of the Bounty.

    Returns:
        dict: The success key with a boolean value and accompanying error.

    """
    profile_id = request.user.profile.pk if request.user.is_authenticated and getattr(request.user, 'profile', None) else None

    access_token = request.GET.get('token')
    if access_token:
        helper_handle_access_token(request, access_token)
        github_user_data = get_github_user_data(access_token)
        profile = Profile.objects.filter(handle=github_user_data['login']).first()
        profile_id = profile.pk

    if not profile_id:
        return JsonResponse(
            {'error': _('You must be authenticated via github to use this feature!')},
            status=401)

    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        return JsonResponse({'errors': ['Bounty doesn\'t exist!']},
                            status=401)

    try:
        interest = Interest.objects.get(profile_id=profile_id, bounty=bounty)
        record_user_action(request.user, 'stop_work', interest)
        record_bounty_activity(bounty, request.user, 'stop_work')
        bounty.interested.remove(interest)
        interest.delete()
        maybe_market_to_slack(bounty, 'stop_work')
        maybe_market_to_user_slack(bounty, 'stop_work')
        maybe_market_to_user_discord(bounty, 'stop_work')
        maybe_market_to_twitter(bounty, 'stop_work')
    except Interest.DoesNotExist:
        return JsonResponse({
            'errors': [_('You haven\'t expressed interest on this bounty.')],
            'success': False},
            status=401)
    except Interest.MultipleObjectsReturned:
        interest_ids = bounty.interested \
            .filter(
                profile_id=profile_id,
                bounty=bounty
            ).values_list('id', flat=True) \
            .order_by('-created')

        bounty.interested.remove(*interest_ids)
        Interest.objects.filter(pk__in=list(interest_ids)).delete()

    return JsonResponse({
        'success': True,
        'msg': _("You've stopped working on this, thanks for letting us know."),
    })


@csrf_exempt
@require_POST
def extend_expiration(request, bounty_id):
    """Extend expiration of the Bounty.

    Can only be called by funder or staff of the bounty.

    :request method: POST

    post_id (int): ID of the Bounty.

    Returns:
        dict: The success key with a boolean value and accompanying error.

    """
    user = request.user if request.user.is_authenticated else None

    if not user:
        return JsonResponse(
            {'error': _('You must be authenticated via github to use this feature!')},
            status=401)

    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        return JsonResponse({'errors': ['Bounty doesn\'t exist!']},
                            status=401)

    is_funder = bounty.is_funder(user.username.lower()) if user else False
    if is_funder:
        deadline = round(int(request.POST.get('deadline')) / 1000)
        bounty.expires_date = timezone.make_aware(
            timezone.datetime.fromtimestamp(deadline),
            timezone=UTC)
        bounty.save()
        record_user_action(request.user, 'extend_expiration', bounty)
        record_bounty_activity(bounty, request.user, 'extend_expiration')

        return JsonResponse({
            'success': True,
            'msg': _("You've extended expiration of this issue."),
        })

    return JsonResponse({
        'error': _("You must be funder to extend expiration"),
    }, status=200)


@csrf_exempt
@require_POST
def cancel_reason(request):
    """Extend expiration of the Bounty.

    Can only be called by funder or staff of the bounty.

    :request method: POST

    Params:
        pk (int): ID of the Bounty.
        canceled_bounty_reason (string): STRING with cancel  reason

    Returns:
        dict: The success key with a boolean value and accompanying error.

    """
    print(request.POST.get('canceled_bounty_reason'))
    user = request.user if request.user.is_authenticated else None

    if not user:
        return JsonResponse(
            {'error': _('You must be authenticated via github to use this feature!')},
            status=401)

    try:
        bounty = Bounty.objects.get(pk=request.POST.get('pk'))
    except Bounty.DoesNotExist:
        return JsonResponse({'errors': ['Bounty doesn\'t exist!']},
                            status=401)

    is_funder = bounty.is_funder(user.username.lower()) if user else False
    if is_funder:
        canceled_bounty_reason = request.POST.get('canceled_bounty_reason', '')
        bounty.canceled_bounty_reason = canceled_bounty_reason
        bounty.save()

        return JsonResponse({
            'success': True,
            'msg': _("Cancel reason added."),
        })

    return JsonResponse({
        'error': _("You must be funder to add a reason"),
    }, status=200)


@require_POST
@csrf_exempt
def uninterested(request, bounty_id, profile_id):
    """Remove party from given bounty

    Can only be called by the bounty funder

    :request method: GET

    Args:
        bounty_id (int): ID of the Bounty
        profile_id (int): ID of the interested profile

    Params:
        slashed (str): if the user will be slashed or not

    Returns:
        dict: The success key with a boolean value and accompanying error.
    """
    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        return JsonResponse({'errors': ['Bounty doesn\'t exist!']},
                            status=401)
    is_logged_in = request.user.is_authenticated
    is_funder = bounty.is_funder(request.user.username.lower())
    is_staff = request.user.is_staff
    is_moderator = request.user.profile.is_moderator if hasattr(request.user, 'profile') else False
    if not is_logged_in or (not is_funder and not is_staff and not is_moderator):
        return JsonResponse(
            {'error': 'Only bounty funders are allowed to remove users!'},
            status=401)

    slashed = request.POST.get('slashed')
    interest = None
    try:
        interest = Interest.objects.get(profile_id=profile_id, bounty=bounty)
        bounty.interested.remove(interest)
        maybe_market_to_slack(bounty, 'stop_work')
        maybe_market_to_user_slack(bounty, 'stop_work')
        maybe_market_to_user_discord(bounty, 'stop_work')
        if is_staff or is_moderator:
            event_name = "bounty_removed_slashed_by_staff" if slashed else "bounty_removed_by_staff"
        else:
            event_name = "bounty_removed_by_funder"
        record_user_action_on_interest(interest, event_name, None)
        record_bounty_activity(bounty, interest.profile.user, 'stop_work')
        interest.delete()
    except Interest.DoesNotExist:
        return JsonResponse({
            'errors': ['Party haven\'t expressed interest on this bounty.'],
            'success': False},
            status=401)
    except Interest.MultipleObjectsReturned:
        interest_ids = bounty.interested \
            .filter(
                profile_id=profile_id,
                bounty=bounty
            ).values_list('id', flat=True) \
            .order_by('-created')

        bounty.interested.remove(*interest_ids)
        Interest.objects.filter(pk__in=list(interest_ids)).delete()

    profile = Profile.objects.get(id=profile_id)
    if profile.user and profile.user.email and interest:
        bounty_uninterested(profile.user.email, bounty, interest)
    else:
        print("no email sent -- user was not found")

    return JsonResponse({
        'success': True,
        'msg': _("You've stopped working on this, thanks for letting us know."),
    })


def onboard_avatar(request):
    return redirect('/onboard/contributor?steps=avatar')


def onboard(request, flow):
    """Handle displaying the first time user experience flow."""
    if flow not in ['funder', 'contributor', 'profile']:
        raise Http404
    elif flow == 'funder':
        onboard_steps = ['github', 'metamask', 'avatar']
    elif flow == 'contributor':
        onboard_steps = ['github', 'metamask', 'avatar', 'skills', 'job']
    elif flow == 'profile':
        onboard_steps = ['avatar']

    profile = None
    if request.user.is_authenticated and getattr(request.user, 'profile', None):
        profile = request.user.profile

    steps = []
    if request.GET:
        steps = request.GET.get('steps', [])
        if steps:
            steps = steps.split(',')

    if (steps and 'github' not in steps) or 'github' not in onboard_steps:
        if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
            request.user, 'profile', None
        ):
            login_redirect = redirect('/login/github?next=' + request.get_full_path())
            return login_redirect

    if request.GET.get('eth_address') and request.user.is_authenticated and getattr(request.user, 'profile', None):
        profile = request.user.profile
        eth_address = request.GET.get('eth_address')
        profile.preferred_payout_address = eth_address
        profile.save()
        return JsonResponse({'OK': True})

    params = {
        'title': _('Onboarding Flow'),
        'steps': steps or onboard_steps,
        'flow': flow,
        'profile': profile,
    }
    params.update(get_avatar_context_for_user(request.user))
    return TemplateResponse(request, 'ftux/onboard.html', params)


def dashboard(request):
    """Handle displaying the dashboard."""

    keyword = request.GET.get('keywords', False)
    title = keyword.title() + str(_(" Bounties ")) if keyword else str(_('Issue Explorer'))
    params = {
        'active': 'dashboard',
        'title': title,
        'meta_title': "Issue & Open Bug Bounty Explorer | Gitcoin",
        'meta_description': "Find open bug bounties & freelance development jobs including crypto bounty reward value in USD, expiration date and bounty age.",
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'dashboard/index.html', params)


def accept_bounty(request):
    """Process the bounty.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The accept bounty view.

    """
    bounty = handle_bounty_views(request)
    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='accept_bounty',
        title=_('Process Issue'),
    )
    params['open_fulfillments'] = bounty.fulfillments.filter(accepted=False)
    return TemplateResponse(request, 'process_bounty.html', params)


def contribute(request):
    """Contribute to the bounty.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The accept bounty view.

    """
    bounty = handle_bounty_views(request)

    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='contribute_bounty',
        title=_('Contribute'),
    )
    return TemplateResponse(request, 'contribute_bounty.html', params)


def invoice(request):
    """invoice view.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The invoice  view.

    """
    bounty = handle_bounty_views(request)

    # only allow invoice viewing if admin or iff bounty funder
    is_funder = bounty.is_funder(request.user.username)
    is_staff = request.user.is_staff
    has_view_privs = is_funder or is_staff
    if not has_view_privs:
        raise Http404

    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='invoice_view',
        title=_('Invoice'),
    )
    params['accepted_fulfillments'] = bounty.fulfillments.filter(accepted=True)
    params['tips'] = [
        tip for tip in bounty.tips.send_happy_path() if tip.username == request.user.username and tip.username
    ]
    params['total'] = bounty._val_usd_db if params['accepted_fulfillments'] else 0
    for tip in params['tips']:
        if tip.value_in_usdt:
            params['total'] += tip.value_in_usdt

    return TemplateResponse(request, 'bounty/invoice.html', params)


def social_contribution(request):
    """Social Contributuion to the bounty.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The accept bounty view.

    """
    bounty = handle_bounty_views(request)
    promo_text = str(_("Check out this bounty that pays out ")) + f"{bounty.get_value_true} {bounty.token_name} {bounty.url}"
    for keyword in bounty.keywords_list:
        promo_text += f" #{keyword}"

    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='social_contribute',
        title=_('Social Contribute'),
    )
    params['promo_text'] = promo_text
    return TemplateResponse(request, 'social_contribution.html', params)


def social_contribution_modal(request):
    # TODO: will be changed to the new share
    """Social Contributuion to the bounty.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The accept bounty view.

    """
    bounty = handle_bounty_views(request)
    promo_text = str(_("Check out this bounty that pays out ")) + f"{bounty.get_value_true} {bounty.token_name} {bounty.url}"
    for keyword in bounty.keywords_list:
        promo_text += f" #{keyword}"

    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='social_contribute',
        title=_('Social Contribute'),
    )
    params['promo_text'] = promo_text
    return TemplateResponse(request, 'social_contribution_modal.html', params)

@csrf_exempt
@require_POST
def social_contribution_email(request):
    """Social Contribution Email

    Returns:
        JsonResponse: Success in sending email.
    """
    from marketing.mails import share_bounty

    print (request.POST.getlist('usersId[]', []))
    emails = [] 
    user_ids = request.POST.getlist('usersId[]', [])
    for user_id in user_ids:
        profile = Profile.objects.get(id=int(user_id))
        emails.append(profile.email)
    msg = request.POST.get('msg', '')
    try:
        share_bounty(emails, msg, request.user.profile)
        response = {
            'status': 200,
            'msg': 'email_sent',
        }
    except Exception as e:
        logging.exception(e)
        response = {
            'status': 500,
            'msg': 'Email not sent',
        }
    return JsonResponse(response)


def payout_bounty(request):
    """Payout the bounty.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The accept bounty view.

    """
    bounty = handle_bounty_views(request)

    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='payout_bounty',
        title=_('Payout'),
    )
    return TemplateResponse(request, 'payout_bounty.html', params)


def bulk_payout_bounty(request):
    """Payout the bounty.

    Args:
        pk (int): The primary key of the bounty to be accepted.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The accept bounty view.

    """
    bounty = handle_bounty_views(request)

    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='payout_bounty',
        title=_('Advanced Payout'),
    )

    return TemplateResponse(request, 'bulk_payout_bounty.html', params)


@require_GET
def fulfill_bounty(request):
    """Fulfill a bounty.

    Parameters:
        pk (int): The primary key of the Bounty.
        standard_bounties_id (int): The standard bounties ID of the Bounty.
        network (str): The network of the Bounty.
        githubUsername (str): The Github Username of the referenced user.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The fulfill bounty view.

    """
    bounty = handle_bounty_views(request)
    if not bounty.has_started_work(request.user.username):
        raise PermissionDenied
    params = get_context(
        ref_object=bounty,
        github_username=request.GET.get('githubUsername'),
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='fulfill_bounty',
        title=_('Submit Work'),
    )
    return TemplateResponse(request, 'bounty/fulfill.html', params)


def increase_bounty(request):
    """Increase a bounty as the funder.

    Args:
        pk (int): The primary key of the bounty to be increased.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The increase bounty view.

    """
    bounty = handle_bounty_views(request)
    user = request.user if request.user.is_authenticated else None
    is_funder = bounty.is_funder(user.username.lower()) if user else False

    params = get_context(
        ref_object=bounty,
        user=user,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='increase_bounty',
        title=_('Increase Bounty'),
    )

    params['is_funder'] = json.dumps(is_funder)

    return TemplateResponse(request, 'bounty/increase.html', params)


def cancel_bounty(request):
    """Kill an expired bounty.

    Args:
        pk (int): The primary key of the bounty to be cancelled.

    Raises:
        Http404: The exception is raised if no associated Bounty is found.

    Returns:
        TemplateResponse: The cancel bounty view.

    """
    bounty = handle_bounty_views(request)
    params = get_context(
        ref_object=bounty,
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='kill_bounty',
        title=_('Cancel Bounty'),
    )
    return TemplateResponse(request, 'bounty/kill.html', params)


def helper_handle_admin_override_and_hide(request, bounty):
    admin_override_and_hide = request.GET.get('admin_override_and_hide', False)
    if admin_override_and_hide:
        is_moderator = request.user.profile.is_moderator if hasattr(request.user, 'profile') else False
        if getattr(request.user, 'profile', None) and is_moderator or request.user.is_staff:
            bounty.admin_override_and_hide = True
            bounty.save()
            messages.success(request, _('Bounty is now hidden'))
        else:
            messages.warning(request, _('Only moderators may do this.'))


def helper_handle_admin_contact_funder(request, bounty):
    admin_contact_funder_txt = request.GET.get('admin_contact_funder', False)
    if admin_contact_funder_txt:
        is_staff = request.user.is_staff
        is_moderator = request.user.profile.is_moderator if hasattr(request.user, 'profile') else False
        if is_staff or is_moderator:
            # contact funder
            admin_contact_funder(bounty, admin_contact_funder_txt, request.user)
            messages.success(request, _(f'Bounty message has been sent'))
        else:
            messages.warning(request, _('Only moderators or the funder of this bounty may do this.'))


def helper_handle_mark_as_remarket_ready(request, bounty):
    admin_mark_as_remarket_ready = request.GET.get('admin_toggle_as_remarket_ready', False)
    if admin_mark_as_remarket_ready:
        is_staff = request.user.is_staff
        is_moderator = request.user.profile.is_moderator if hasattr(request.user, 'profile') else False
        if is_staff or is_moderator:
            bounty.admin_mark_as_remarket_ready = not bounty.admin_mark_as_remarket_ready
            bounty.save()
            if bounty.admin_mark_as_remarket_ready:
                messages.success(request, _(f'Bounty is now remarket ready'))
            else:
                messages.success(request, _(f'Bounty is now NOT remarket ready'))
        else:
            messages.warning(request, _('Only moderators or the funder of this bounty may do this.'))


def helper_handle_suspend_auto_approval(request, bounty):
    suspend_auto_approval = request.GET.get('suspend_auto_approval', False)
    if suspend_auto_approval:
        is_staff = request.user.is_staff
        is_moderator = request.user.profile.is_moderator if hasattr(request.user, 'profile') else False
        if is_staff or is_moderator:
            bounty.admin_override_suspend_auto_approval = True
            bounty.save()
            messages.success(request, _(f'Bounty auto approvals are now suspended'))
        else:
            messages.warning(request, _('Only moderators or the funder of this bounty may do this.'))


def helper_handle_override_status(request, bounty):
    admin_override_satatus = request.GET.get('admin_override_satatus', False)
    if admin_override_satatus:
        is_staff = request.user.is_staff
        if is_staff:
            valid_statuses = [ele[0] for ele in Bounty.STATUS_CHOICES]
            valid_statuses = valid_statuses + [""]
            valid_statuses_str = ",".join(valid_statuses)
            if admin_override_satatus not in valid_statuses:
                messages.warning(request, str(
                    _('Not a valid status choice.  Please choose a valid status (no quotes): ')) + valid_statuses_str)
            else:
                bounty.override_status = admin_override_satatus
                bounty.save()
                messages.success(request, _(f'Status updated to "{admin_override_satatus}" '))
        else:
            messages.warning(request, _('Only staff or the funder of this bounty may do this.'))


def helper_handle_snooze(request, bounty):
    snooze_days = int(request.GET.get('snooze', 0))
    if snooze_days:
        is_funder = bounty.is_funder(request.user.username.lower())
        is_staff = request.user.is_staff
        is_moderator = request.user.profile.is_moderator if hasattr(request.user, 'profile') else False
        if is_funder or is_staff or is_moderator:
            bounty.snooze_warnings_for_days = snooze_days
            bounty.save()
            messages.success(request, _(f'Warning messages have been snoozed for {snooze_days} days'))
        else:
            messages.warning(request, _('Only moderators or the funder of this bounty may do this.'))


def helper_handle_approvals(request, bounty):
    mutate_worker_action = request.GET.get('mutate_worker_action', None)
    mutate_worker_action_past_tense = 'approved' if mutate_worker_action == 'approve' else 'rejected'
    worker = request.GET.get('worker', None)

    if mutate_worker_action:
        if not request.user.is_authenticated:
            messages.warning(request, _('You must be logged in to approve or reject worker submissions. Please login and try again.'))
            return

        if not worker:
            messages.warning(request, _('You must provide the worker\'s username in order to approve or reject them.'))
            return

        is_funder = bounty.is_funder(request.user.username.lower())
        is_staff = request.user.is_staff
        if is_funder or is_staff:
            pending_interests = bounty.interested.select_related('profile').filter(profile__handle=worker, pending=True)
            # Check whether or not there are pending interests.
            if not pending_interests.exists():
                messages.warning(
                    request,
                    _('This worker does not exist or is not in a pending state. Perhaps they were already approved or rejected? Please check your link and try again.'))
                return
            interest = pending_interests.first()

            if mutate_worker_action == 'approve':
                interest.pending = False
                interest.acceptance_date = timezone.now()
                interest.save()

                start_work_approved(interest, bounty)

                maybe_market_to_github(bounty, 'work_started', profile_pairs=bounty.profile_pairs)
                maybe_market_to_slack(bounty, 'worker_approved')
                maybe_market_to_user_slack(bounty, 'worker_approved')
                maybe_market_to_twitter(bounty, 'worker_approved')
                record_bounty_activity(bounty, request.user, 'worker_approved', interest)
            else:
                start_work_rejected(interest, bounty)

                record_bounty_activity(bounty, request.user, 'worker_rejected', interest)
                bounty.interested.remove(interest)
                interest.delete()

                maybe_market_to_slack(bounty, 'worker_rejected')
                maybe_market_to_user_slack(bounty, 'worker_rejected')
                maybe_market_to_twitter(bounty, 'worker_rejected')

            messages.success(request, _(f'{worker} has been {mutate_worker_action_past_tense}'))
        else:
            messages.warning(request, _('Only the funder of this bounty may perform this action.'))


def bounty_invite_url(request, invitecode):
    """Decode the bounty details and redirect to correct bounty

    Args:
        invitecode (str): Unique invite code with bounty details and handle
    
    Returns:
        django.template.response.TemplateResponse: The Bounty details template response.
    """
    decoded_data = get_bounty_from_invite_url(invitecode)
    bounty = Bounty.objects.current().filter(pk=decoded_data['bounty_id'])
    return redirect('/funding/details/?url=' + bounty.github_url)
    


def bounty_details(request, ghuser='', ghrepo='', ghissue=0, stdbounties_id=None):
    """Display the bounty details.

    Args:
        ghuser (str): The Github user. Defaults to an empty string.
        ghrepo (str): The Github repository. Defaults to an empty string.
        ghissue (int): The Github issue number. Defaults to: 0.

    Raises:
        Exception: The exception is raised for any exceptions in the main query block.

    Returns:
        django.template.response.TemplateResponse: The Bounty details template response.

    """
    from .utils import clean_bounty_url
    is_user_authenticated = request.user.is_authenticated
    request_url = clean_bounty_url(request.GET.get('url', ''))
    if is_user_authenticated and hasattr(request.user, 'profile'):
        _access_token = request.user.profile.get_access_token()
    else:
        _access_token = request.session.get('access_token')
    issue_url = 'https://github.com/' + ghuser + '/' + ghrepo + '/issues/' + ghissue if ghissue else request_url

    # try the /pulls url if it doesn't exist in /issues
    try:
        assert Bounty.objects.current().filter(github_url=issue_url).exists()
    except Exception:
        issue_url = 'https://github.com/' + ghuser + '/' + ghrepo + '/pull/' + ghissue if ghissue else request_url

    params = {
        'issueURL': issue_url,
        'title': _('Issue Details'),
        'card_title': _('Funded Issue Details | Gitcoin'),
        'avatar_url': static('v2/images/helmet.png'),
        'active': 'bounty_details',
        'is_github_token_valid': is_github_token_valid(_access_token),
        'github_auth_url': get_auth_url(request.path),
        "newsletter_headline": _("Be the first to know about new funded issues."),
        'is_staff': request.user.is_staff,
        'is_moderator': request.user.profile.is_moderator if hasattr(request.user, 'profile') else False,
    }
    if issue_url:
        try:
            bounties = Bounty.objects.current().filter(github_url=issue_url)
            stdbounties_id = clean_str(stdbounties_id)
            if stdbounties_id and stdbounties_id.isdigit():
                bounties = bounties.filter(standard_bounties_id=stdbounties_id)
            if bounties:
                bounty = bounties.order_by('-pk').first()
                if bounties.count() > 1 and bounties.filter(network='mainnet').count() > 1:
                    bounty = bounties.filter(network='mainnet').order_by('-pk').first()
                # Currently its not finding anyting in the database
                if bounty.title and bounty.org_name:
                    params['card_title'] = f'{bounty.title} | {bounty.org_name} Funded Issue Detail | Gitcoin'
                    params['title'] = params['card_title']
                    params['card_desc'] = ellipses(bounty.issue_description_text, 255)

                params['bounty_pk'] = bounty.pk
                params['network'] = bounty.network
                params['stdbounties_id'] = bounty.standard_bounties_id if not stdbounties_id else stdbounties_id
                params['interested_profiles'] = bounty.interested.select_related('profile').all()
                params['avatar_url'] = bounty.get_avatar_url(True)

                helper_handle_snooze(request, bounty)
                helper_handle_approvals(request, bounty)
                helper_handle_admin_override_and_hide(request, bounty)
                helper_handle_suspend_auto_approval(request, bounty)
                helper_handle_mark_as_remarket_ready(request, bounty)
                helper_handle_admin_contact_funder(request, bounty)
                helper_handle_override_status(request, bounty)
        except Bounty.DoesNotExist:
            pass
        except Exception as e:
            logger.error(e)

    return TemplateResponse(request, 'bounty/details.html', params)


def funder_payout_reminder_modal(request, bounty_network, stdbounties_id):
    bounty = Bounty.objects.current().filter(network=bounty_network, standard_bounties_id=stdbounties_id).first()

    context = {
        'bounty': bounty,
        'active': 'funder_payout_reminder_modal',
        'title': _('Send Payout Reminder')
    }
    return TemplateResponse(request, 'funder_payout_reminder_modal.html', context)


@csrf_exempt
def funder_payout_reminder(request, bounty_network, stdbounties_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'You must be authenticated via github to use this feature!'},
            status=401)

    if hasattr(request.user, 'profile'):
        access_token = request.user.profile.get_access_token()
    else:
        access_token = request.session.get('access_token')
    github_user_data = get_github_user_data(access_token)

    try:
        bounty = Bounty.objects.current().filter(network=bounty_network, standard_bounties_id=stdbounties_id).first()
    except Bounty.DoesNotExist:
        raise Http404

    has_fulfilled = bounty.fulfillments.filter(fulfiller_github_username=github_user_data['login']).count()
    if has_fulfilled == 0:
        return JsonResponse({
            'success': False,
          },
          status=403)

    #  410 Gone Indicates that the resource requested is no longer available and will not be available again.
    if bounty.funder_last_messaged_on:
        return JsonResponse({
            'success': False,
          },
          status=410)

    user = request.user
    funder_payout_reminder_mail(to_email=bounty.bounty_owner_email, bounty=bounty, github_username=user, live=True)
    bounty.funder_last_messaged_on = timezone.now()
    bounty.save()
    return JsonResponse({
          'success': True
        },
        status=200)


def quickstart(request):
    """Display quickstart guide."""
    return TemplateResponse(request, 'quickstart.html', {})


def profile_keywords(request, handle):
    """Display profile keywords.

    Args:
        handle (str): The profile handle.

    """
    try:
        profile = profile_helper(handle, True)
    except (ProfileNotFoundException, ProfileHiddenException):
        raise Http404

    response = {
        'status': 200,
        'keywords': profile.keywords,
    }
    return JsonResponse(response)


@require_POST
def profile_job_opportunity(request, handle):
    """ Save profile job opportunity.

    Args:
        handle (str): The profile handle.
    """
    try:
        profile = profile_helper(handle, True)
        profile.job_search_status = request.POST.get('job_search_status', None)
        profile.show_job_status = request.POST.get('show_job_status', None) == 'true'
        profile.job_type = request.POST.get('job_type', None)
        profile.remote = request.POST.get('remote', None) == 'on'
        profile.job_salary = float(request.POST.get('job_salary', '0').replace(',', ''))
        profile.job_location = json.loads(request.POST.get('locations'))
        profile.linkedin_url = request.POST.get('linkedin_url', None)
        profile.resume = request.FILES.get('job_cv', None)
        profile.save()
    except (ProfileNotFoundException, ProfileHiddenException):
        raise Http404

    response = {
        'status': 200,
        'message': 'Job search status saved'
    }
    return JsonResponse(response)


def profile_filter_activities(activities, activity_name):
    """A helper function to filter a ActivityQuerySet.

    Args:
        activities (ActivityQuerySet): The ActivityQuerySet.
        activity_name (str): The activity_type to filter.

    Returns:
        ActivityQuerySet: The filtered results.

    """
    if not activity_name or activity_name == 'all':
        return activities
    if activity_name == 'start_work':
        return activities.filter(activity_type__in=['start_work', 'worker_approved'])
    return activities.filter(activity_type=activity_name)


def profile(request, handle):
    """Display profile details.

    Args:
        handle (str): The profile handle.

    Variables:
        context (dict): The template context to be used for template rendering.
        profile (dashboard.models.Profile): The Profile object to be used.
        status (int): The status code of the response.

    Returns:
        TemplateResponse: The profile templated view.

    """
    status = 200
    order_by = request.GET.get('order_by', '-modified_on')
    owned_kudos = None
    sent_kudos = None
    handle = handle.replace("@", "")

    try:
        if not handle and not request.user.is_authenticated:
            return redirect('funder_bounties')

        if not handle:
            handle = request.user.username
            profile = getattr(request.user, 'profile', None)
            if not profile:
                profile = profile_helper(handle)
        else:
            if handle.endswith('/'):
                handle = handle[:-1]
            profile = profile_helper(handle, current_user=request.user)

        activity_tabs = [
            ('all', _('All Activity')),
            ('new_bounty', _('Bounties Funded')),
            ('start_work', _('Work Started')),
            ('work_submitted', _('Work Submitted')),
            ('work_done', _('Bounties Completed')),
            ('new_tip', _('Tips Sent')),
            ('receive_tip', _('Tips Received')),
        ]
        page = request.GET.get('p', None)

        if page:
            page = int(page)
            activity_type = request.GET.get('a', '')
            all_activities = profile.get_bounty_and_tip_activities()
            paginator = Paginator(profile_filter_activities(all_activities, activity_type), 10)

            if page > paginator.num_pages:
                return HttpResponse(status=204)

            context = {}
            context['activities'] = paginator.get_page(page)

            return TemplateResponse(request, 'profiles/profile_activities.html', context, status=status)

        context = profile.to_dict(tips=False)
        all_activities = context.get('activities')
        tabs = []

        for tab, name in activity_tabs:
            activities = profile_filter_activities(all_activities, tab)
            activities_count = activities.count()

            if activities_count == 0:
                continue

            paginator = Paginator(activities, 10)

            obj = {'id': tab,
                   'name': name,
                   'objects': paginator.get_page(1),
                   'count': activities_count,
                   'type': 'activity'
                   }
            tabs.append(obj)

            context['tabs'] = tabs

    except (Http404, ProfileHiddenException, ProfileNotFoundException):
        status = 404
        context = {
            'hidden': True,
            'profile': {
                'handle': handle,
                'avatar_url': f"/dynamic/avatar/Self",
                'data': {
                    'name': f"@{handle}",
                },
            },
        }
        return TemplateResponse(request, 'profiles/profile.html', context, status=status)

    context['preferred_payout_address'] = profile.preferred_payout_address

    owned_kudos = profile.get_my_kudos.order_by('id', order_by)
    sent_kudos = profile.get_sent_kudos.order_by('id', order_by)
    kudos_limit = 8
    context['kudos'] = owned_kudos[0:kudos_limit]
    context['sent_kudos'] = sent_kudos[0:kudos_limit]
    context['kudos_count'] = owned_kudos.count()
    context['sent_kudos_count'] = sent_kudos.count()
    context['verification'] = profile.get_my_verified_check

    currently_working_bounties = Bounty.objects.current().filter(interested__profile=profile).filter(interested__status='okay') \
        .filter(interested__pending=False).filter(idx_status__in=Bounty.WORK_IN_PROGRESS_STATUSES)
    currently_working_bounties_count = currently_working_bounties.count()
    if currently_working_bounties_count > 0:
        obj = {'id': 'currently_working',
               'name': _('Currently Working'),
               'objects': Paginator(currently_working_bounties, 10).get_page(1),
               'count': currently_working_bounties_count,
               'type': 'bounty'
               }
        if 'tabs' not in context:
            context['tabs'] = []
        context['tabs'].append(obj)

    if request.method == 'POST' and request.is_ajax():
        # Update profile address data when new preferred address is sent
        validated = request.user.is_authenticated and request.user.username.lower() == profile.handle.lower()
        if validated and request.POST.get('address'):
            address = request.POST.get('address')
            profile.preferred_payout_address = address
            profile.save()
            msg = {
                'status': 200,
                'msg': _('Success!'),
                'wallets': [profile.preferred_payout_address, ],
            }

            return JsonResponse(msg, status=msg.get('status', 200))
    return TemplateResponse(request, 'profiles/profile.html', context, status=status)


@csrf_exempt
def lazy_load_kudos(request):
    page = request.POST.get('page', 1)
    context = {}
    datarequest = request.POST.get('request')
    order_by = request.GET.get('order_by', '-modified_on')
    limit = int(request.GET.get('limit', 8))
    handle = request.POST.get('handle')

    if handle:
        try:
            profile = Profile.objects.get(handle=handle)
            if datarequest == 'mykudos':
                key = 'kudos'
                context[key] = profile.get_my_kudos.order_by('id', order_by)
            else:
                key = 'sent_kudos'
                context[key] = profile.get_sent_kudos.order_by('id', order_by)
        except Profile.DoesNotExist:
            pass

    paginator = Paginator(context[key], limit)
    kudos = paginator.get_page(page)
    html_context = {}
    html_context[key] = kudos
    html_context['kudos_data'] = key
    kudos_html = loader.render_to_string('shared/kudos_card_profile.html', html_context)
    return JsonResponse({'kudos_html': kudos_html, 'has_next': kudos.has_next()})


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def get_quickstart_video(request):
    """Show quickstart video."""
    context = {
        'active': 'video',
        'title': _('Quickstart Video'),
    }
    return TemplateResponse(request, 'quickstart_video.html', context)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def extend_issue_deadline(request):
    """Show quickstart video."""
    bounty = Bounty.objects.get(pk=request.GET.get("pk"))
    print(bounty)
    context = {
        'active': 'extend_issue_deadline',
        'title': _('Extend Expiration'),
        'bounty': bounty,
        'user_logged_in': request.user.is_authenticated,
        'login_link': '/login/github?next=' + request.GET.get('redirect', '/')
    }
    return TemplateResponse(request, 'extend_issue_deadline.html', context)


@require_POST
@csrf_exempt
@ratelimit(key='ip', rate='5/s', method=ratelimit.UNSAFE, block=True)
def sync_web3(request):
    """Sync up web3 with the database.

    This function has a few different uses.  It is typically called from the
    front end using the javascript `sync_web3` function.  The `issueURL` is
    passed in first, followed optionally by a `bountydetails` argument.

    Returns:
        JsonResponse: The JSON response following the web3 sync.

    """
    # setup
    result = {
        'status': '400',
        'msg': "bad request"
    }

    issue_url = request.POST.get('url')
    txid = request.POST.get('txid')
    network = request.POST.get('network')

    if issue_url and txid and network:
        # confirm txid has mined
        print('* confirming tx has mined')
        if not has_tx_mined(txid, network):
            result = {
                'status': '400',
                'msg': 'tx has not mined yet'
            }
        else:

            # get bounty id
            print('* getting bounty id')
            bounty_id = get_bounty_id(issue_url, network)
            if not bounty_id:
                result = {
                    'status': '400',
                    'msg': 'could not find bounty id'
                }
            else:
                # get/process bounty
                print('* getting bounty')
                bounty = get_bounty(bounty_id, network)
                print('* processing bounty')
                did_change = False
                max_tries_attempted = False
                counter = 0
                url = None
                while not did_change and not max_tries_attempted:
                    did_change, _, new_bounty = web3_process_bounty(bounty)
                    if not did_change:
                        print("RETRYING")
                        time.sleep(3)
                        counter += 1
                        max_tries_attempted = counter > 3
                    if new_bounty:
                        url = new_bounty.url
                result = {
                    'status': '200',
                    'msg': "success",
                    'did_change': did_change,
                    'url': url,
                }

    return JsonResponse(result, status=result['status'])


# LEGAL
@xframe_options_exempt
def terms(request):
    context = {
        'title': _('Terms of Use'),
    }
    return TemplateResponse(request, 'legal/terms.html', context)


def privacy(request):
    return TemplateResponse(request, 'legal/privacy.html', {})


def cookie(request):
    return TemplateResponse(request, 'legal/privacy.html', {})


def prirp(request):
    return TemplateResponse(request, 'legal/privacy.html', {})


def apitos(request):
    return TemplateResponse(request, 'legal/privacy.html', {})


def toolbox(request):
    access_token = request.GET.get('token')
    if access_token and is_github_token_valid(access_token):
        helper_handle_access_token(request, access_token)

    tools = Tool.objects.prefetch_related('votes').all()

    actors = [{
        "title": _("Basics"),
        "description": _("Accelerate your dev workflow with Gitcoin\'s incentivization tools."),
        "tools": tools.filter(category=Tool.CAT_BASIC)
    }, {
        "title": _("Community"),
        "description": _("Friendship, mentorship, and community are all part of the process."),
        "tools": tools.filter(category=Tool.CAT_COMMUNITY)
    }, {
        "title": _("Gas Tools"),
        "description": _("Paying Gas is a part of using Ethereum.  It's much easier with our suite of gas tools."),
        "tools": tools.filter(category=Tool.GAS_TOOLS)
    }, {
        "title": _("Developer Tools"),
        "description": _("Gitcoin is a platform that's built using Gitcoin.  Purdy cool, huh? "),
        "tools": tools.filter(category=Tool.CAT_BUILD)
    }, {
        "title": _("Tools in Alpha"),
        "description": _("These fresh new tools are looking for someone to test ride them!"),
        "tools": tools.filter(category=Tool.CAT_ALPHA)
    }, {
        "title": _("Just for Fun"),
        "description": _("Some tools that the community built *just because* they should exist."),
        "tools": tools.filter(category=Tool.CAT_FOR_FUN)
    }, {
        "title": _("Advanced"),
        "description": _("Take your OSS game to the next level!"),
        "tools": tools.filter(category=Tool.CAT_ADVANCED)
    }, {
        "title": _("Roadmap"),
        "description": _("These ideas have been floating around the community.  They'll be BUIDLt sooner if you help BUIDL them :)"),
        "tools": tools.filter(category=Tool.CAT_COMING_SOON)
    }, {
        "title": _("Retired Tools"),
        "description": _("These are tools that we've sunsetted.  Pour one out for them 🍻"),
        "tools": tools.filter(category=Tool.CAT_RETIRED)
    }]

    # setup slug
    for key in range(0, len(actors)):
        actors[key]['slug'] = slugify(actors[key]['title'])

    profile_up_votes_tool_ids = ''
    profile_down_votes_tool_ids = ''
    profile_id = request.user.profile.pk if request.user.is_authenticated and hasattr(request.user, 'profile') else None

    if profile_id:
        ups = list(request.user.profile.votes.filter(value=1).values_list('tool', flat=True))
        profile_up_votes_tool_ids = ','.join(str(x) for x in ups)
        downs = list(request.user.profile.votes.filter(value=-1).values_list('tool', flat=True))
        profile_down_votes_tool_ids = ','.join(str(x) for x in downs)

    context = {
        "active": "tools",
        'title': _("Tools"),
        'card_title': _("Community Tools"),
        'avatar_url': static('v2/images/tools/api.jpg'),
        "card_desc": _("Accelerate your dev workflow with Gitcoin\'s incentivization tools."),
        'actors': actors,
        'newsletter_headline': _("Don't Miss New Tools!"),
        'profile_up_votes_tool_ids': profile_up_votes_tool_ids,
        'profile_down_votes_tool_ids': profile_down_votes_tool_ids
    }
    return TemplateResponse(request, 'toolbox.html', context)


def labs(request):
    labs = LabsResearch.objects.all()
    tools = Tool.objects.prefetch_related('votes').filter(category=Tool.CAT_ALPHA)

    socials = [{
        "name": _("GitHub Repo"),
        "link": "https://github.com/gitcoinco/labs/",
        "class": "fab fa-github fa-2x"
    }, {
        "name": _("Slack"),
        "link": "https://gitcoin.co/slack",
        "class": "fab fa-slack fa-2x"
    }, {
        "name": _("Contact the Team"),
        "link": "mailto:founders@gitcoin.co",
        "class": "fa fa-envelope fa-2x"
    }]

    context = {
        'active': "labs",
        'title': _("Labs"),
        'card_desc': _("Gitcoin Labs provides advanced tools for busy developers"),
        'avatar_url': 'https://c.gitcoin.co/labs/Articles-Announcing_Gitcoin_Labs.png',
        'tools': tools,
        'labs': labs,
        'socials': socials
    }
    return TemplateResponse(request, 'labs.html', context)


@csrf_exempt
@require_POST
def vote_tool_up(request, tool_id):
    profile_id = request.user.profile.pk if request.user.is_authenticated and hasattr(request.user, 'profile') else None
    if not profile_id:
        return JsonResponse(
            {'error': 'You must be authenticated via github to use this feature!'},
            status=401)

    tool = Tool.objects.get(pk=tool_id)
    score_delta = 0
    try:
        vote = ToolVote.objects.get(profile_id=profile_id, tool=tool)
        if vote.value == 1:
            vote.delete()
            score_delta = -1
        if vote.value == -1:
            vote.value = 1
            vote.save()
            score_delta = 2
    except ToolVote.DoesNotExist:
        vote = ToolVote.objects.create(profile_id=profile_id, value=1)
        tool.votes.add(vote)
        score_delta = 1
    return JsonResponse({'success': True, 'score_delta': score_delta})


@csrf_exempt
@require_POST
def vote_tool_down(request, tool_id):
    profile_id = request.user.profile.pk if request.user.is_authenticated and hasattr(request.user, 'profile') else None
    if not profile_id:
        return JsonResponse(
            {'error': 'You must be authenticated via github to use this feature!'},
            status=401)

    tool = Tool.objects.get(pk=tool_id)
    score_delta = 0
    try:
        vote = ToolVote.objects.get(profile_id=profile_id, tool=tool)
        if vote.value == -1:
            vote.delete()
            score_delta = 1
        if vote.value == 1:
            vote.value = -1
            vote.save()
            score_delta = -2
    except ToolVote.DoesNotExist:
        vote = ToolVote.objects.create(profile_id=profile_id, value=-1)
        tool.votes.add(vote)
        score_delta = -1
    return JsonResponse({'success': True, 'score_delta': score_delta})


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def redeem_coin(request, shortcode):
    if request.body:
        status = 'OK'

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        address = body['address']

        try:
            coin = CoinRedemption.objects.get(shortcode=shortcode)
            address = Web3.toChecksumAddress(address)

            if hasattr(coin, 'coinredemptionrequest'):
                status = 'error'
                message = 'Bad request'
            else:
                abi = json.loads('[{"constant":true,"inputs":[],"name":"mintingFinished","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_subtractedValue","type":"uint256"}],"name":"decreaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"finishMinting","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_addedValue","type":"uint256"}],"name":"increaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"payable":false,"stateMutability":"nonpayable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[],"name":"MintFinished","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]')

                # Instantiate Colorado Coin contract
                contract = w3.eth.contract(coin.contract_address, abi=abi)

                tx = contract.functions.transfer(address, coin.amount * 10**18).buildTransaction({
                    'nonce': w3.eth.getTransactionCount(settings.COLO_ACCOUNT_ADDRESS),
                    'gas': 100000,
                    'gasPrice': recommend_min_gas_price_to_confirm_in_time(5) * 10**9
                })

                signed = w3.eth.account.signTransaction(tx, settings.COLO_ACCOUNT_PRIVATE_KEY)
                transaction_id = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

                CoinRedemptionRequest.objects.create(
                    coin_redemption=coin,
                    ip=get_ip(request),
                    sent_on=timezone.now(),
                    txid=transaction_id,
                    txaddress=address
                )

                message = transaction_id
        except CoinRedemption.DoesNotExist:
            status = 'error'
            message = _('Bad request')
        except Exception as e:
            status = 'error'
            message = str(e)

        # http response
        response = {
            'status': status,
            'message': message,
        }

        return JsonResponse(response)

    try:
        coin = CoinRedemption.objects.get(shortcode=shortcode)

        params = {
            'class': 'redeem',
            'title': _('Coin Redemption'),
            'coin_status': _('PENDING')
        }

        try:
            coin_redeem_request = CoinRedemptionRequest.objects.get(coin_redemption=coin)
            params['colo_txid'] = coin_redeem_request.txid
        except CoinRedemptionRequest.DoesNotExist:
            params['coin_status'] = _('INITIAL')

        return TemplateResponse(request, 'yge/redeem_coin.html', params)
    except CoinRedemption.DoesNotExist:
        raise Http404


def new_bounty(request):
    """Create a new bounty."""
    from .utils import clean_bounty_url
    bounty_params = {
        'newsletter_headline': _('Be the first to know about new funded issues.'),
        'issueURL': clean_bounty_url(request.GET.get('source') or request.GET.get('url', '')),
        'amount': request.GET.get('amount'),
    }

    params = get_context(
        user=request.user if request.user.is_authenticated else None,
        confirm_time_minutes_target=confirm_time_minutes_target,
        active='submit_bounty',
        title=_('Create Funded Issue'),
        update=bounty_params,
    )
    return TemplateResponse(request, 'bounty/new.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def change_bounty(request, bounty_id):
    user = request.user if request.user.is_authenticated else None

    if not user:
        if request.body:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)
        else:
            return redirect('/login/github?next=' + request.get_full_path())

    try:
        bounty_id = int(bounty_id)
        bounty = Bounty.objects.get(pk=bounty_id)
    except:
        if request.body:
            return JsonResponse({'error': _('Bounty doesn\'t exist!')}, status=404)
        else:
            raise Http404

    keys = ['experience_level', 'project_length', 'bounty_type', 'featuring_date',
            'permission_type', 'project_type', 'reserved_for_user_handle', 'is_featured']

    if request.body:
        can_change = (bounty.status in Bounty.OPEN_STATUSES) or \
                (bounty.can_submit_after_expiration_date and bounty.status is 'expired')
        if not can_change:
            return JsonResponse({
                'error': _('The bounty can not be changed anymore.')
            }, status=405)

        is_funder = bounty.is_funder(user.username.lower()) if user else False
        is_staff = request.user.is_staff if user else False
        if not is_funder and not is_staff:
            return JsonResponse({
                'error': _('You are not authorized to change the bounty.')
            }, status=401)

        try:
            params = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        bounty_changed = False
        new_reservation = False
        for key in keys:
            value = params.get(key, 0)
            if key == 'featuring_date':
                value = timezone.make_aware(
                    timezone.datetime.fromtimestamp(int(value)),
                    timezone=UTC)
            old_value = getattr(bounty, key)
            if value != old_value:
                setattr(bounty, key, value)
                bounty_changed = True
                if key == 'reserved_for_user_handle' and value:
                    new_reservation = True

        if not bounty_changed:
            return JsonResponse({
                'success': True,
                'msg': _('Bounty details are unchanged.'),
                'url': bounty.absolute_url,
            })

        bounty.save()
        record_bounty_activity(bounty, user, 'bounty_changed')
        record_user_action(user, 'bounty_changed', bounty)

        maybe_market_to_email(bounty, 'bounty_changed')
        maybe_market_to_slack(bounty, 'bounty_changed')
        maybe_market_to_user_slack(bounty, 'bounty_changed')
        maybe_market_to_user_discord(bounty, 'bounty_changed')

        # notify a user that a bounty has been reserved for them
        if new_reservation and bounty.bounty_reserved_for_user:
            new_reserved_issue('founders@gitcoin.co', bounty.bounty_reserved_for_user, bounty)

        return JsonResponse({
            'success': True,
            'msg': _('You successfully changed bounty details.'),
            'url': bounty.absolute_url,
        })

    result = {}
    for key in keys:
        result[key] = getattr(bounty, key)
    del result['featuring_date']

    params = {
        'title': _('Change Bounty Details'),
        'pk': bounty.pk,
        'result': json.dumps(result)
    }
    return TemplateResponse(request, 'bounty/change.html', params)


def get_users(request):
    token = request.GET.get('token', None)
    add_non_gitcoin_users = not request.GET.get('suppress_non_gitcoiners', None)

    if request.is_ajax():
        q = request.GET.get('term')
        profiles = Profile.objects.filter(handle__icontains=q)
        results = []
        # try gitcoin
        for user in profiles:
            profile_json = {}
            profile_json['id'] = user.id
            profile_json['text'] = user.handle
            profile_json['email'] = user.email
            if user.avatar_baseavatar_related.exists():
                profile_json['avatar_id'] = user.avatar_baseavatar_related.first().pk
                profile_json['avatar_url'] = user.avatar_baseavatar_related.first().avatar_url
            profile_json['preferred_payout_address'] = user.preferred_payout_address
            results.append(profile_json)
        # try github
        if not len(results) and add_non_gitcoin_users:
            search_results = search_users(q, token=token)
            for result in search_results:
                profile_json = {}
                profile_json['id'] = -1
                profile_json['text'] = result.login
                profile_json['email'] = None
                profile_json['avatar_id'] = None
                profile_json['avatar_url'] = result.avatar_url
                profile_json['preferred_payout_address'] = None
                # dont dupe github profiles and gitcoin profiles in user search
                if profile_json['text'].lower() not in [p['text'].lower() for p in profiles]:
                    results.append(profile_json)
        # just take users word for it
        if not len(results) and add_non_gitcoin_users:
            profile_json = {}
            profile_json['id'] = -1
            profile_json['text'] = q
            profile_json['email'] = None
            profile_json['avatar_id'] = None
            profile_json['preferred_payout_address'] = None
            results.append(profile_json)
        data = json.dumps(results)
    else:
        raise Http404
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def get_kudos(request):
    autocomplete_kudos = {
        'copy': "No results found.  Try these categories: ",
        'autocomplete': ['rare','common','ninja','soft skills','programming']
    }
    if request.is_ajax():
        q = request.GET.get('term')
        network = request.GET.get('network', None)
        eth_to_usd = convert_token_to_usdt('ETH')
        kudos_by_name = Token.objects.filter(name__icontains=q)
        kudos_by_desc = Token.objects.filter(description__icontains=q)
        kudos_by_tags = Token.objects.filter(tags__icontains=q)
        kudos_pks = (kudos_by_desc | kudos_by_name | kudos_by_tags).values_list('pk', flat=True)
        kudos = Token.objects.filter(pk__in=kudos_pks, hidden=False, num_clones_allowed__gt=0).order_by('name')
        is_staff = request.user.is_staff if request.user.is_authenticated else False
        if not is_staff:
            kudos = kudos.filter(send_enabled_for_non_gitcoin_admins=True)
        if network:
            kudos = kudos.filter(contract__network=network)
        results = []
        for token in kudos:
            kudos_json = {}
            kudos_json['id'] = token.id
            kudos_json['token_id'] = token.token_id
            kudos_json['name'] = token.name
            kudos_json['name_human'] = humanize_name(token.name)
            kudos_json['description'] = token.description
            kudos_json['image'] = token.image

            kudos_json['price_finney'] = token.price_finney / 1000
            kudos_json['price_usd'] = eth_to_usd * kudos_json['price_finney']
            kudos_json['price_usd_humanized'] = f"${round(kudos_json['price_usd'], 2)}"

            results.append(kudos_json)
        if not results:
            results = [autocomplete_kudos]
        data = json.dumps(results)
    else:
        raise Http404
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
