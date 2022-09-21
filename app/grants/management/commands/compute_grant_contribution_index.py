from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import F

import pytz
from grants.models import Contribution, Grant, GrantContributionIndex, Subscription
from grants.models.grant import GrantCLR


class Command(BaseCommand):

    help = "Rebuilds the table GrantContributionIndex"

    def handle(self, *args, **kwargs):
        self.stdout.write(f"{datetime.now()} Building query for contributions ...")

        # Set the max date for which we want to collect the data for
        to_date = datetime(2022, 9, 7, 15, 0, 0, tzinfo=pytz.UTC)

        # Get the existing round number information
        grant_clrs = list(
            GrantCLR.objects.distinct("round_num").values_list(
                "round_num", "start_date", "end_date"
            )
        )

        def get_round_num(created_on):
            for r in grant_clrs:
                if r[1] < created_on and created_on < r[2]:
                    return r[0]
            return None

        # Query to get all cnotributions
        contributions = (
            Contribution.objects.filter(
                success=True,
                subscription__network="mainnet",
                subscription__contributor_profile__isnull=False,
                created_on__lt=to_date,
            )
            .order_by("id")
            .distinct("id")
            .values_list(
                "id",
                "profile_for_clr_id",
                "subscription__grant__id",
                "amount_per_period_usdt",
                "created_on",
            )
        )

        # Determine the round number (if any) of each contribution
        self.stdout.write(f"{datetime.now()} Adding round_num to results")
        contributions = [
            (c0, c1, c2, c3, created_on, get_round_num(created_on))
            for (c0, c1, c2, c3, created_on) in contributions
        ]
        self.stdout.write(f"{datetime.now()} Got {len(contributions)} contributions")

        self.stdout.write(f"{datetime.now()} Building contribIndexList ...")
        contribIndexList = [
            GrantContributionIndex(
                contribution_id=contribution_id,
                profile_id=profile_id,
                round_num=round_num,
                grant_id=grant_id,
                amount=amount,
            )
            for contribution_id, profile_id, grant_id, amount, _, round_num  in contributions
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

        for i in range(0, count, batch_size):
            self.stdout.write(
                f"{datetime.now()} {(i / count * 100):.2f}% Saving to GrantContributionIndex ..."
            )
            GrantContributionIndex.objects.bulk_create(
                contribIndexList[i : i + batch_size], ignore_conflicts=True
            )
