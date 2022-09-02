import traceback
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import numpy as np
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
    stamps_from_db = PassportStamp.objects.values("user_id", "stamp_provider")
    if stamps_from_db:
        df = pd.DataFrame(stamps_from_db)
    else:
        df = pd.DataFrame.from_dict(
            {
                "user_id": [],
                "stamp_provider": [],
            }
        )

    df_stamps_processed_from_db = GR15TrustScore.objects.values("user_id", "stamps")
    if df_stamps_processed_from_db:
        df_stamps_processed_last_calculation_round = pd.DataFrame(
            df_stamps_processed_from_db
        )
    else:
        df_stamps_processed_last_calculation_round = pd.DataFrame.from_dict(
            {
                "user_id": [],
                "stamps": [],
            }
        )

    df_user_stamp_list = df.groupby("user_id")["stamp_provider"].apply(list)
    print("User stamp list:\n", df_user_stamp_list)

    df_stamps = df.copy()
    df_stamps["is_stamp_preserved"] = 1
    df_stamps_processed_last_calculation_round = df_stamps_processed_last_calculation_round.explode("stamps")
    # Drop any rows that will contain NaN provider (these users have no stamps)
    df_stamps_processed_last_calculation_round.dropna(inplace=True)
    print(
        "===> df_stamps_processed_last_calculation_round:\n",
        df_stamps_processed_last_calculation_round,
    )
    # Merge:
    #   - left - the stamps processed last time
    #   - right - all the current stamps
    #   - how='outer'  => this will get us empty cells in the columns of the left
    #       dataset, which will indicate stamps that have been removed
    # And we will add a column which is_stamp_preserved will contain 1 is the stamp was present in the previous calc, 0 otherwise
    df_stamp_overview = df_stamps_processed_last_calculation_round.merge(
        df_stamps,
        how="outer",
        left_on=["user_id", "stamps"],
        right_on=["user_id", "stamp_provider"],
    )

    print("===> df_stamp_overview:\n", df_stamp_overview)
    # Set the value of is_stamp_preserved to 0, in cases where a stamp has been removed compared to the previous calculatioin
    df_stamp_overview.loc[
        df_stamp_overview.is_stamp_preserved != 1, "is_stamp_preserved"
    ] = 0

    # df["is_stamp_preserved"] = df_stamp_overview.is_stamp_preserved

    print("df_stamp_overview:\n", df_stamp_overview)

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
        df_stamp_overview[p] = 0
        df_stamp_overview.loc[df_stamp_overview["stamp_provider"] == p, p] = 1

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
    aggregation_rule = {k: "max" for k in providers}

    def list_exclude_nan(iterable):
        return list([x for x in iterable if not pd.isna(x)])

    # We will exclude the nan values from the list of providers, we'll only store the new valid ones
    aggregation_rule["stamp_provider"] = list_exclude_nan
    # is_stamp_preserved will contain 1 is the stamp was present in the previous calc, 0 otherwise
    # we want to identify the users that had a stamp removed (we will recalculate the trust bonus even this means lowering the score)
    # By applying min, we identify thoses users (as they end up having 0)
    aggregation_rule["is_stamp_preserved"] = min
    prepared_df = df_stamp_overview.groupby(["user_id"]).agg(aggregation_rule)
    print("=" * 40)
    print("prepared_df\n", prepared_df)
    print("=" * 40)
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
    # df_existing_gr15_scores.set_index("user_id", inplace=True)
    # df_apu_scores.set_index("user_id", inplace=True)

    # Create a new boolean column to mark the records coming from DB (to be used after join, to separate
    # new records from records to be updated)
    df_existing_gr15_scores["from_db"] = True

    apu_median = df_apu_scores["Score"].median()
    apu_min = df_apu_scores["Score"].min()
    print("APU median: %s" % apu_median)
    print("APU min: %s" % apu_min)

    df_gr15_scores = df_existing_gr15_scores.join(df_apu_scores, how="outer")

    # Ensure valid values in Score. NaN might occur for users that have removed all thei stamps
    df_gr15_scores.Score.fillna(0.0, inplace=True)
    df_gr15_scores.has_removed_stamps.fillna(False, inplace=True)
    df_gr15_scores.current_stamps.fillna("", inplace=True)

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
    new_trust_bonus.replace([np.inf, -np.inf], 0, inplace=True)
    df_gr15_scores.trust_bonus.fillna(0.0, inplace=True)

    print("-----------------")
    print("new_trust_bonus", new_trust_bonus)
    print("-----------------")
    print("df_gr15_scores.trust_bonus", df_gr15_scores.trust_bonus)
    print("-----------------")

    update_trust_bonus_condition = (df_gr15_scores.has_removed_stamps == True) | (
        new_trust_bonus > df_gr15_scores.trust_bonus
    )

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

            df_apu_scores.set_index("user_id", inplace=True)
            prepared_df.set_index("user_id", inplace=True)
            # This will initialize all NaNs with []  (see https://stackoverflow.com/a/64207857)
            print("===>df_apu_scores\n", df_apu_scores)
            print("===>prepared_df\n", prepared_df)

            df_t = pd.DataFrame(
                {
                    "current_stamps": prepared_df.stamp_provider,
                    "has_removed_stamps": (1 - prepared_df.is_stamp_preserved).astype(
                        "bool"
                    ),
                },
                index=prepared_df.index,
            )
            print("===>df_t\n", df_t)

            df_apu_scores = df_apu_scores.merge(
                df_t, how="outer", left_index=True, right_index=True
            )

            # df_apu_scores["current_stamps"] = prepared_df.stamp_provider
            # df_apu_scores["current_stamps"].fillna("HELLO", inplace=True)
            # df_apu_scores["has_removed_stamps"] = (
            #     1 - prepared_df.is_stamp_preserved
            # )  # Just invert the logic here
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
                "stamps",
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
                        "stamps": [[]],
                    }
                )

            df_existing_gr15_scores.set_index("user_id", inplace=True)
            df_gr15_scores = calculate_trust_bonus(
                df_existing_gr15_scores, df_apu_scores
            )

            # Drop any records with no current_stamps
            # df_gr15_scores.dropna(subset=["current_stamps"], inplace=True)
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
                    stamps=data.current_stamps,
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
                    stamps=data.current_stamps,
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
                    "user_id",
                    "last_apu_score",
                    "max_apu_score",
                    "trust_bonus",
                    "last_apu_calculation_time",
                    "max_apu_calculation_time",
                    "trust_bonus_calculation_time",
                    "stamps",
                ],
            )
        except Exception as exc:
            self.stdout.write(self.style.ERROR('ERROR: "%s"' % exc))
            # printing stack trace
            traceback.print_exc()
            raise CommandError("An unexpected error occured")
