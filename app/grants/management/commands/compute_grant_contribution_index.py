import datetime as dt
from datetime import timezone
from time import sleep

from django.core.management.base import BaseCommand

import requests
from grants.models import Contribution, GrantContributionIndex


class Command(BaseCommand):

    help = "rebuilds the table GrantContributionIndex"

    def handle(self, *args, **kwargs):
        contributions = (
            Contribution.objects.filter(
                success=True,
                subscription__network="mainnet",
                subscription__grant__clr_calculations__latest=True,
            )
            .order_by(
                "subscription__contributor_profile__id",
                "subscription__grant__clr_calculations__grantclr__round_num",
                "subscription__grant__id",
            )
            .distinct(
                "subscription__contributor_profile__id",
                "subscription__grant__clr_calculations__grantclr__round_num",
                "subscription__grant__id",
            )
            .values_list(
                "subscription__contributor_profile__id",
                "subscription__grant__clr_calculations__grantclr__round_num",
                "subscription__grant__id",
            )
        )

        contribIndexList = [
            GrantContributionIndex(
                profile_id=contribInfo[0],
                grant_id=contribInfo[1],
                round_num=contribInfo[2],
            )
            for contribInfo in contributions
        ]

        GrantContributionIndex.objects.bulk_create(contribIndexList, batch_size=100)
