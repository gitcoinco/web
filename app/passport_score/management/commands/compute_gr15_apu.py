import traceback
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import pandas as pd
from dashboard.models import PassportStamp
from passport_score.models import GR15TrustScore

MAX_TRUST_BONUS = 1.5
MIN_TRUST_BONUS = 0.5


def load_passport_stamps():
    stamps = list(PassportStamp.objects.all().values("user_id", "stamp_provider"))
    df = pd.DataFrame(stamps)

    print(df)
    df["stamp_provider"] = df.stamp_provider.str.lower()

    providers = [p for p in df.stamp_provider.unique() if p]

    for p in providers:
        df[p] = 0
        df.loc[df["stamp_provider"] == p, p] = 1

    prepared_df = df.groupby(["user_id"]).max()
    prepared_df.reset_index(inplace=True)

    grouping_fields_1 = ["user_id"]
    grouping_fields = []

    return (prepared_df, providers, grouping_fields, grouping_fields_1)


class Command(BaseCommand):
    help = "Calculates the APU score for GR15 based on the currently submitted passports & stamps"

    def handle(self, *args, **options):
        # delay import as this is only available in newer envs ...
        from passport_score.gr15_scorer import compute_apu_scores

        try:
            ###################################################################################
            # Load the data and compute the APU score
            ###################################################################################

            self.stdout.write("Loading passport stamps")

            (
                prepared_df,
                stamp_fields,
                grouping_fields,
                grouping_fields_1,
            ) = load_passport_stamps()

            self.stdout.write("Running scorer")
            scores = compute_apu_scores(
                prepared_df, stamp_fields, grouping_fields, grouping_fields_1
            )

            scores.set_index("user_id")
            self.stdout.write("\nScores: \n%s" % scores)

            ###################################################################################
            # Evaluate the APU score, apply the trust bonus calculation
            ###################################################################################
            # Load existing scores from the DB
            existing_gr15_scores = GR15TrustScore.objects.values(
                "id",
                "user_id",
                "last_apu_score",
                "max_apu_score",
                "trust_bonus",
                "last_apu_calculation_time",
                "max_apu_calculation_time",
            )

            # Create a DataFrame for the data, handle the case when the dataset loaded from DB is empty
            if existing_gr15_scores:
                # Create dataframe from DB results
                df_existing_gr15_scores = pd.DataFrame(existing_gr15_scores)
            else:
                # Create an empty dataframe, if no results where loaded from DB
                df_existing_gr15_scores = pd.DataFrame.from_dict(
                    {
                        "id": [],
                        "user_id": [],
                        "last_apu_score": [],
                        "max_apu_score": [],
                        "trust_bonus": [],
                        "last_apu_calculation_time": [],
                        "max_apu_calculation_time": [],
                    }
                )

            # Set the user_id as index, as we will join on that
            df_existing_gr15_scores.set_index("user_id", inplace=True)
            scores.set_index("user_id", inplace=True)

            # Create a new boolean column to mark the records coming from DB (to be used after join, to separate
            # new records from records to be updated)
            df_existing_gr15_scores["from_db"] = True

            apu_median = scores["Score"].median()
            apu_min = scores["Score"].min()
            self.stdout.write("APU median: %s" % apu_median)

            df_gr15_scores = df_existing_gr15_scores.join(scores, how="outer")

            self.stdout.write(
                "\nInitial scores summary (including db records): \n%s" % df_gr15_scores
            )

            # Update records ....
            now = timezone.now()
            df_gr15_scores.last_apu_score = df_gr15_scores.Score
            df_gr15_scores.last_apu_calculation_time = now

            max_apus_to_update = (pd.isnull(df_gr15_scores.max_apu_score)) | (
                df_gr15_scores.last_apu_score > df_gr15_scores.max_apu_score
            )
            df_gr15_scores.loc[
                max_apus_to_update,
                "max_apu_score",
            ] = df_gr15_scores.last_apu_score
            df_gr15_scores.loc[
                max_apus_to_update,
                "max_apu_calculation_time",
            ] = now

            # Set the trust bonus to 1.5 for user who have now gone anove median
            df_gr15_scores.loc[
                (df_gr15_scores.trust_bonus < MAX_TRUST_BONUS)
                & (df_gr15_scores.last_apu_score >= apu_median),
                "trust_bonus",
            ] = MAX_TRUST_BONUS

            # Linear interpolation for users who have an APU score < median
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # Note: the trust bonus might end up NaN if apu_median - apu_min == 0 
            # as sthis will lead to division by 0
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            df_gr15_scores.loc[
                (df_gr15_scores.trust_bonus < MAX_TRUST_BONUS)
                & (df_gr15_scores.last_apu_score < apu_median),
                "trust_bonus",
            ] = (df_gr15_scores.last_apu_score - apu_min) / (apu_median - apu_min) * (
                MAX_TRUST_BONUS - MIN_TRUST_BONUS
            ) + MIN_TRUST_BONUS

            self.stdout.write(
                "\nRecords after trust bonus recalculation: \n%s" % df_gr15_scores
            )

            ###################################################################################
            # Write the new scores back to the DB
            ###################################################################################
            # Determine the records to be created in the DB (for new users that have submitted their passport) and the ones to be created
            # for user_id, data in df_gr15_scores.iterrows():
            #     print(data.last_apu_calculation_time)
            #     print(data.max_apu_calculation_time)
            #     print(data.last_apu_calculation_time.to_dat)
            #     print(data.max_apu_calculation_time)

            # return

            new_records = [
                GR15TrustScore(
                    user_id=user_id,
                    last_apu_score=data.last_apu_score,
                    max_apu_score=data.max_apu_score,
                    trust_bonus=data.trust_bonus,
                    last_apu_calculation_time=data.last_apu_calculation_time,
                    max_apu_calculation_time=data.max_apu_calculation_time,
                )
                for user_id, data in df_gr15_scores.loc[
                    df_gr15_scores.from_db != True
                ].iterrows()
            ]

            records_from_db = [
                GR15TrustScore(
                    id=data.id,
                    user_id=user_id,
                    last_apu_score=data.last_apu_score,
                    max_apu_score=data.max_apu_score,
                    trust_bonus=data.trust_bonus,
                    last_apu_calculation_time=data.last_apu_calculation_time,
                    max_apu_calculation_time=data.max_apu_calculation_time,
                )
                for user_id, data in df_gr15_scores.loc[
                    df_gr15_scores.from_db == True
                ].iterrows()
            ]

            self.stdout.write("\nRecords to be updated: \n%s" % records_from_db)
            self.stdout.write("\nNew records to be created: \n%s" % new_records)

            # Bulk creating new records
            self.stdout.write(
                "\nBulk creating new records (count=%s)\n" % len(new_records)
            )
            GR15TrustScore.objects.bulk_create(new_records)

            # Bulk updating existing records
            self.stdout.write(
                "\nBulk updating existing records (count=%s)\n" % len(records_from_db)
            )
            GR15TrustScore.objects.bulk_update(
                records_from_db,
                [
                    "last_apu_score",
                    "max_apu_score",
                    "trust_bonus",
                    "last_apu_calculation_time",
                    "max_apu_calculation_time",
                ],
            )
        except Exception as exc:
            self.stdout.write(self.style.ERROR('ERROR: "%s"' % exc))
            # printing stack trace
            traceback.print_exc()
            raise CommandError("An unexpected error occured")
