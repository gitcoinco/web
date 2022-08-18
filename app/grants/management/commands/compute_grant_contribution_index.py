import datetime as dt
from datetime import datetime, timezone
from time import sleep

from django.core.management.base import BaseCommand
from django.db.models import F

import requests
from grants.models import Contribution, Grant, GrantContributionIndex


class Command(BaseCommand):

    help = "rebuilds the table GrantContributionIndex"

    def handle(self, *args, **kwargs):
        self.stdout.write(f"{datetime.now()} Building query for contributions ...")
        contributions = (
            Contribution.objects.filter(
                success=True,
                subscription__network="mainnet",
                subscription__grant__clr_calculations__latest=True,
                subscription__contributor_profile__isnull=False,
                created_on__gt=F(
                    "subscription__grant__clr_calculations__grantclr__start_date"
                ),
                created_on__lt=F(
                    "subscription__grant__clr_calculations__grantclr__end_date"
                ),
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

        self.stdout.write(f"{datetime.now()} Building contribIndexList ...")
        contribIndexList = [
            GrantContributionIndex(
                profile_id=contribInfo[0],
                round_num=contribInfo[1],
                grant_id=contribInfo[2],
            )
            for contribInfo in contributions
        ]

        count = len(contribIndexList)
        self.stdout.write(f"{datetime.now()} Length of contribIndexList: {count}")
        self.stdout.write(f"{datetime.now()} Clearing GrantContributionIndex ...")

        first_id = 0
        last_id = 0

        try:
            first_id = GrantContributionIndex.objects.all().order_by("id")[0].id
            last_id = GrantContributionIndex.objects.all().order_by("-id")[0].id
        except:
            pass

        self.stdout.write(
            f"{datetime.now()} ... deleting {last_id - first_id + 1} records"
        )

        count_to_delete = last_id - first_id
        count_deleted = 0
        batch_size = 50000
        for i in range(first_id, last_id, batch_size):
            count_deleted += batch_size
            self.stdout.write(
                f"{datetime.now()} ... {(count_deleted / count_to_delete * 100):.2f}% deleting {count} records up to id {i + batch_size}"
            )
            GrantContributionIndex.objects.filter(id__lt=i + batch_size).delete()

        self.stdout.write(f"{datetime.now()} Saving to GrantContributionIndex ...")
        # GrantContributionIndex.objects.bulk_create(contribIndexList, batch_size=1000, ignore_conflicts=True)
        for i in range(0, count, batch_size):
            self.stdout.write(
                f"{datetime.now()} {(i / count * 100):.2f}% Saving to GrantContributionIndex ..."
            )
            GrantContributionIndex.objects.bulk_create(
                contribIndexList[i : i + batch_size], ignore_conflicts=True
            )
