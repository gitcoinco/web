import traceback
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import pandas as pd
from dashboard.models import PassportStamp
from passport_score.gr15_providers import providers
from passport_score.models import GR15TrustScore

MAX_TRUST_BONUS = 1.5
MIN_TRUST_BONUS = 0.5


def load_passport_stamps():
    """
    Load stamps from the grants database & prepares the data for input into the GR15 scoring algorithm
    """

    # Load stamps and store them into a dataframe
    stamps = list(PassportStamp.objects.all().values("user_id", "stamp_provider"))
    df = pd.DataFrame(stamps)

    print("stamps", df)

    # Get list of all unique provider names
    # providers = [p for p in df.stamp_provider.unique() if p]
    print("Providers: ", providers)
    print("Providers count: ", len(providers))

    # Insert a column for each provider, set 0 as default and 1 if the user owns that stamp
    # Example:
    #     user_id   stamp_provider     google facebook twitter      ...
    #     1         google              1      0        0
    #     1         facebook            0      1        0
    #     1         twitter             0      0        1
    #     2         google              1      0        0
    #     3         facebook            0      1        0
    #     3         twitter             0      0        1
    #   ...
    for p in providers:
        df[p] = 0
        df.loc[df["stamp_provider"] == p, p] = 1

    # Group by user_id, performing max aggrgation withina group.
    # The result will be that we have 1 row per user, and  each row will contain the
    # following in the specific provider columns:
    #       0 if the user DOES NOT HAVE that stamp
    #       1 if the user has that stamp
    # The example from above becomes:
    #     user_id   google facebook twitter      ...
    #     1          1      1        1
    #     2          1      0        0
    #     3          0      1        1
    #   ...
    prepared_df = df.groupby(["user_id"]).max()
    prepared_df.reset_index(inplace=True)

    # Reset the index, we want to have the user_id as separate column
    grouping_fields_1 = ["user_id"]

    # TODO: grouping_fields - not sure why this is for, we could probably remove it ...
    grouping_fields = []

    return (prepared_df, providers, grouping_fields, grouping_fields_1)


def calculate_trust_bonus(df_existing_gr15_scores, df_apu_scores):
    """Calculate the new trust bonus score based on:

    df_existing_gr15_scores - the current set of records from the DB (the previous run)
    df_apu_scores - the newly computed APU scores
    """
    # Set the user_id as index, as we will join on that
    df_existing_gr15_scores.set_index("user_id", inplace=True)
    df_apu_scores.set_index("user_id", inplace=True)

    # Create a new boolean column to mark the records coming from DB (to be used after join, to separate
    # new records from records to be updated)
    df_existing_gr15_scores["from_db"] = True

    apu_median = df_apu_scores["Score"].median()
    apu_min = df_apu_scores["Score"].min()
    print("APU median: %s" % apu_median)

    df_gr15_scores = df_existing_gr15_scores.join(df_apu_scores, how="outer")

    # Ensure valid values in Score. NaN might occur for users that have removed all thei stamps
    df_gr15_scores.Score.fillna(0.0, inplace=True)

    print("\nInitial scores summary (including db records): \n%s" % df_gr15_scores)

    # Update records ....
    now = timezone.now()
    df_gr15_scores.last_apu_score = df_gr15_scores.Score
    df_gr15_scores.last_apu_calculation_time = now

    print("last_apu_score:", df_gr15_scores.last_apu_score)
    print("max_apu_score:", df_gr15_scores.max_apu_score)

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

    # Linear interpolation for users who have an APU score < median
    # Users with score above median get the max trust bonus
    # !!! AND !!!: we never store a trust_bonus score smaller than in the previous calculation (i. e. loaded from db)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Note: the trust bonus might end up NaN if apu_median - apu_min == 0
    # as this will lead to division by 0
    # We are setting the trust_bonus to 0 in this case
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    new_trust_bonus = (df_gr15_scores.last_apu_score - apu_min) / (
        apu_median - apu_min
    ) * (MAX_TRUST_BONUS - MIN_TRUST_BONUS) + MIN_TRUST_BONUS

    # Ensure max trust bonus
    new_trust_bonus.clip(upper=1.5, inplace=True)

    # Ensure valid values (eliminate NaNs)
    new_trust_bonus.fillna(0.0, inplace=True)
    df_gr15_scores.trust_bonus.fillna(0.0, inplace=True)

    print("-----------------")
    print("new_trust_bonus", new_trust_bonus)
    print("-----------------")
    print("df_gr15_scores.trust_bonus", df_gr15_scores.trust_bonus)
    print("-----------------")

    update_trust_bonus_condition = new_trust_bonus > df_gr15_scores.trust_bonus

    df_gr15_scores.loc[
        update_trust_bonus_condition,
        "trust_bonus",
    ] = new_trust_bonus.loc[update_trust_bonus_condition]
    df_gr15_scores.loc[
        update_trust_bonus_condition,
        "trust_bonus_calculation_time",
    ] = now

    # Fill any null values in the trust_bonus_calculation_time
    df_gr15_scores.trust_bonus_calculation_time.fillna(now, inplace=True)

    print("\nRecords after trust bonus recalculation: \n%s" % df_gr15_scores)
    return df_gr15_scores


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
            df_apu_scores = compute_apu_scores(
                prepared_df, stamp_fields, grouping_fields, grouping_fields_1
            )

            df_apu_scores.set_index("user_id")
            self.stdout.write("\nScores: \n%s" % df_apu_scores)

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
                "trust_bonus_calculation_time",
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
                        "trust_bonus_calculation_time": [],
                    }
                )

            df_gr15_scores = calculate_trust_bonus(
                df_existing_gr15_scores, df_apu_scores
            )

            self.stdout.write("\nNew scores & trust bonus: \n%s" % df_gr15_scores)
            ###################################################################################
            # Write the new scores back to the DB
            ###################################################################################
            # Determine the records to be created in the DB (for new users that have submitted their passport) and the ones to be created
            new_records = [
                GR15TrustScore(
                    user_id=user_id,
                    last_apu_score=data.last_apu_score,
                    max_apu_score=data.max_apu_score,
                    trust_bonus=data.trust_bonus,
                    last_apu_calculation_time=data.last_apu_calculation_time,
                    max_apu_calculation_time=data.max_apu_calculation_time,
                    trust_bonus_calculation_time=data.trust_bonus_calculation_time,
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
                    trust_bonus_calculation_time=data.trust_bonus_calculation_time,
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
