# -*- coding: utf-8 -*-
"""Define the Grant views.

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
import logging

from django.conf import settings
from django.db.models import Sum
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from grants.models import Contribution
from perftools.models import StaticJsonEnv
from townsquare.models import SquelchProfile

logger = logging.getLogger(__name__)


def ami_api_token_required(func):
    def decorator(request, *args, **kwargs):
        try:
            apiToken = StaticJsonEnv.objects.get(key="AMI_API_TOKEN")
            expectedToken = apiToken.data["token"]
            receivedToken = request.headers.get("Authorization")

            if receivedToken:
                # Token shall look like "token <bearer token>", and we need only the <bearer token> part
                receivedToken = receivedToken.split(" ")[1]

            if expectedToken == receivedToken:
                return func(request, *args, **kwargs)
            else:
                return JsonResponse(
                    {
                        "error": "Access denied",
                    },
                    status=403,
                )
        except Exception as e:
            logger.error("Error in ami_api_token_required %s", e)
            return JsonResponse(
                {
                    "error": "An unexpected error occured",
                },
                status=500,
            )

    return decorator


@ami_api_token_required
def contributor_statistics(request):
    handle = request.GET.get("handle")

    if not handle:
        return JsonResponse(
            {"error": "Bad request, 'handle' parameter is missing or invalid"},
            status=400,
        )

    # Get number of grantsthe user contributed to
    grants_count = (
        Contribution.objects.filter(profile_for_clr__handle=handle, success=True)
        .order_by("grant_id")
        .distinct("grant_id")
        .count()
    )

    # Get the number of grants the user contributed to
    rounds_count = (
        Contribution.objects.filter(
            success=True,
            subscription__contributor_profile__handle=handle,
            subscription__network="mainnet",
            subscription__grant__clr_calculations__latest=True,
        )
        .order_by("subscription__grant__clr_calculations__grantclr__round_num")
        .distinct("subscription__grant__clr_calculations__grantclr__round_num")
        .count()
    )

    total_contribution_amount = Contribution.objects.filter(
        profile_for_clr__handle=handle, success=True
    ).aggregate(Sum("amount_per_period_usdt"))["amount_per_period_usdt__sum"]
    total_contribution_amount = total_contribution_amount if total_contribution_amount is not None else 0

    # GR14 contibutor (and not squelched by FDD)
    profile_squelch = SquelchProfile.objects.filter(
        profile__handle=handle, active=True
    ).values_list("profile_id", flat=True)
    
    num_gr14_contributions = (
        Contribution.objects.filter(
            success=True,
            subscription__contributor_profile__handle=handle,
            subscription__network="mainnet",
            subscription__grant__clr_calculations__latest=True,
            subscription__grant__clr_calculations__grantclr__round_num=14,
        )
        .exclude(subscription__contributor_profile_id__in=profile_squelch)
        .count()
    )

    return JsonResponse(
        {
            "grants_count": grants_count,
            "rounds_count": rounds_count,
            "total_contribution_amount": total_contribution_amount,
            "is_gr14_contributor": num_gr14_contributions > 0,
        }
    )
