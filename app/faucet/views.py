# -*- coding: utf-8 -*-
"""Define faucet views.

Copyright (C) 2021 Gitcoin Core

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

"""
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email, validate_slug
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape, strip_tags
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from faucet.models import FaucetRequest
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from marketing.mails import new_faucet_request, processed_faucet_request, reject_faucet_request


@require_GET
def faucet(request):
    params = {
        'title': 'Faucet',
        'card_title': _('Gitcoin Faucet'),
        'card_desc': _('Request a distribution of ETH so you can use the Ethereum network and Gitcoin.'),
        'faucet_amount': settings.FAUCET_AMOUNT
    }

    return TemplateResponse(request, 'faucet_form.html', params)


@csrf_exempt
@require_POST
def save_faucet(request):
    """Handle saving faucet requests."""
    email_address = request.POST.get('emailAddress')
    eth_address = request.POST.get('ethAddress')
    is_authenticated = request.user.is_authenticated
    profile = request.user.profile if is_authenticated and hasattr(request.user, 'profile') else None

    if not profile:
        return JsonResponse({
            'message': _('You must be authenticated via github to use this feature!')
        }, status=401)

    try:
        validate_slug(eth_address)
        if email_address:
            validate_email(email_address)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

    comment = escape(strip_tags(request.POST.get('comment', '')))
    if not profile.trust_profile and profile.github_created_on > (timezone.now() - timezone.timedelta(days=7)):
        return JsonResponse({
            'message': _('For SPAM prevention reasons, you may not perform this action right now.  Please contact support if you believe this message is in error.')
        }, status=403)
    if profile.faucet_requests.filter(fulfilled=True):
        return JsonResponse({
            'message': _('The submitted github profile shows a previous faucet distribution.')
        }, status=403)
    elif profile.faucet_requests.filter(rejected=False):
        return JsonResponse({
            'message': _('The submitted github profile shows a pending faucet distribution.')
        }, status=403)
    fr = FaucetRequest.objects.create(
        fulfilled=False,
        github_username=request.user.username,
        github_meta={},
        address=eth_address,
        email=email_address if email_address else request.user.email,
        comment=comment,
        profile=profile,
    )
    new_faucet_request(fr)

    return JsonResponse({'message': _('Created.')}, status=201)


@require_http_methods(['GET', 'POST'])
@staff_member_required
def process_faucet_request(request, pk):
    try:
        faucet_request = FaucetRequest.objects.get(pk=pk)
    except FaucetRequest.DoesNotExist:
        raise Http404

    redir_link = '/_administrationfaucet/faucetrequest/?fulfilled=f&rejected=f'
    faucet_amount = float(settings.FAUCET_AMOUNT) * float(recommend_min_gas_price_to_confirm_in_time(5))

    if faucet_request.fulfilled:
        messages.info(request, 'already fulfilled')
        return redirect(redir_link)

    if faucet_request.rejected:
        messages.info(request, 'already rejected')
        return redirect(redir_link)

    reject_comments = request.POST.get('reject_comments')
    if reject_comments:
        faucet_request.comment_admin = reject_comments
        faucet_request.rejected = True
        faucet_request.save()
        reject_faucet_request(faucet_request)
        messages.success(request, 'rejected')
        return redirect(redir_link)

    if request.POST.get('destinationAccount'):
        faucet_request.fulfilled = True
        faucet_request.fulfill_date = timezone.now()
        faucet_request.amount = faucet_amount
        faucet_request.save()
        processed_faucet_request(faucet_request)
        messages.success(request, 'sent')
        return redirect(redir_link)

    common_rejection_reasons = [
        "Please tell us what you're planning on using these funds for in the comments section!  Thanks.",
        "This is a faucet for Gitcoin-specific functionality (like posting Bounties or fulfilling Bounties).  Please re-submit your request if you need to do something Gitcoin specific.",
        "You don't need ETH to start work on a bounty.  Please submit another request if you finish your work and need to submit work.",
        "",
    ]

    context = {
        'obj': faucet_request,
        'faucet_amount': faucet_amount,
        'recommend_gas_price': round(recommend_min_gas_price_to_confirm_in_time(1), 1),
        'common_rejection_reasons': common_rejection_reasons,
    }

    return TemplateResponse(request, 'process_faucet_request.html', context)
