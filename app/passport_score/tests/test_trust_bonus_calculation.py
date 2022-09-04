from django.contrib.auth.models import User
from django.utils import timezone

import pandas as pd
import pytest
from passport_score.gr15_providers import providers
from passport_score.management.commands.test_compute_gr15_trust_bonus import calculate_trust_bonus
from test_plus.test import TestCase

CURRENT_USERNAME = "bot_dude"
CURRENT_PASSWORD = "mimamamemima"


APU_SCORES = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

APU_SCORE_MEDIAN = 0.5
APU_SCORE_MIN = 0.05

MAX_TRUST_BONUS = 1.5
MIN_TRUST_BONUS = 0.5

EXPECTED_TRUST_BONUS = [
    (
        (i - APU_SCORE_MIN)
        / (APU_SCORE_MEDIAN - APU_SCORE_MIN)
        * (MAX_TRUST_BONUS - MIN_TRUST_BONUS)
        + MIN_TRUST_BONUS
    )
    if i < APU_SCORE_MEDIAN
    else 1.5
    for i in APU_SCORES
]
NUM_USERS = len(APU_SCORES)


@pytest.mark.django_db
class TestTrustBonusCalculation(TestCase):
    """Test trust bonus alculation."""

    def setUp(self):
        self.users = [
            User.objects.create(password=CURRENT_PASSWORD, username=f"user_{i}")
            for i in range(NUM_USERS)
        ]

    def test_initial_trust_bonus(self):
        """Calculating the trust bonus when GR15TrustScore is empty"""

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
                "stamps": [],
            }
        )
        df_existing_gr15_scores[
            "original_last_apu_score"
        ] = df_existing_gr15_scores.last_apu_score
        df_existing_gr15_scores[
            "original_trust_bonus"
        ] = df_existing_gr15_scores.trust_bonus

        df_apu_scores = pd.DataFrame.from_dict(
            {
                "user_id": [user.id for user in self.users],
                "Score": APU_SCORES,
                "current_stamps": [["Google", "Facebook", "POAP"] for _ in self.users],
                "has_removed_stamps": [False for _ in self.users],
            }
        )

        df_existing_gr15_scores.set_index("user_id", inplace=True)
        df_apu_scores.set_index("user_id", inplace=True)

        df_trust_bonus_calculation = calculate_trust_bonus(
            df_existing_gr15_scores, df_apu_scores
        )

        assert list(df_trust_bonus_calculation.last_apu_score) == list(
            df_apu_scores.Score
        )
        assert list(df_trust_bonus_calculation.trust_bonus) == EXPECTED_TRUST_BONUS

    def test_trust_bonus_does_not_shrink(self):
        """Test that the trust bonus does not shrink for users that have the same (or more) stamps"""

        # This should resulnt in smaller trust bonus being calculated for users at
        # the index: 1, 2, 3, 4 as we reduced their APU and they are below median
        APU_SCORES_REDUCED = [0.05, 0.05, 0.1, 0.1, 0.1, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        df_existing_gr15_scores = pd.DataFrame.from_dict(
            {
                "id": [user.id for user in self.users],
                "user_id": [user.id for user in self.users],
                "last_apu_score": APU_SCORES,
                "max_apu_score": APU_SCORES,
                "trust_bonus": EXPECTED_TRUST_BONUS,
                "last_apu_calculation_time": [timezone.now() for _ in self.users],
                "max_apu_calculation_time": [timezone.now() for _ in self.users],
                "trust_bonus_calculation_time": [timezone.now() for _ in self.users],
                "stamps": ["" for _ in self.users],
            }
        )
        df_existing_gr15_scores[
            "original_last_apu_score"
        ] = df_existing_gr15_scores.last_apu_score
        df_existing_gr15_scores[
            "original_trust_bonus"
        ] = df_existing_gr15_scores.trust_bonus

        df_apu_scores = pd.DataFrame.from_dict(
            {
                "user_id": [user.id for user in self.users],
                "Score": APU_SCORES_REDUCED,
                "current_stamps": [["Google", "Facebook", "POAP"] for _ in self.users],
                "has_removed_stamps": [False for _ in self.users],
            }
        )

        df_existing_gr15_scores.set_index("user_id", inplace=True)
        df_apu_scores.set_index("user_id", inplace=True)

        df_trust_bonus_calculation = calculate_trust_bonus(
            df_existing_gr15_scores, df_apu_scores
        )

        assert list(df_trust_bonus_calculation.last_apu_score) == list(
            df_apu_scores.Score
        )
        # Despite some users having lower APU scores, their trust bonus should not be reduced
        # compare dto the one already save, because they have not removed stamps
        assert list(df_trust_bonus_calculation.trust_bonus) == EXPECTED_TRUST_BONUS

    def test_trust_bonus_shrinks_if_stamps_removed(self):
        """Test that the trust bonus does shrink for users that have had stamps removed"""

        # This should resulnt in smaller trust bonus being calculated for users at
        # the index: 1, 2, 3, 4 as we reduced their APU and they are below median
        APU_SCORES_REDUCED = [0.05, 0.05, 0.1, 0.1, 0.1, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        HAS_REMOVED_STAMPS = [
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        EXPECTED_REDUCED_TRUST_BONUS = [
            (
                (i - APU_SCORE_MIN)
                / (APU_SCORE_MEDIAN - APU_SCORE_MIN)
                * (MAX_TRUST_BONUS - MIN_TRUST_BONUS)
                + MIN_TRUST_BONUS
            )
            if i < APU_SCORE_MEDIAN
            else 1.5
            for i in APU_SCORES_REDUCED
        ]

        df_existing_gr15_scores = pd.DataFrame.from_dict(
            {
                "id": [user.id for user in self.users],
                "user_id": [user.id for user in self.users],
                "last_apu_score": EXPECTED_TRUST_BONUS,
                "max_apu_score": APU_SCORES,
                "trust_bonus": EXPECTED_TRUST_BONUS,
                "last_apu_calculation_time": [timezone.now() for _ in self.users],
                "max_apu_calculation_time": [timezone.now() for _ in self.users],
                "trust_bonus_calculation_time": [timezone.now() for _ in self.users],
                "stamps": ["" for _ in self.users],
            }
        )
        df_existing_gr15_scores[
            "original_last_apu_score"
        ] = df_existing_gr15_scores.last_apu_score
        df_existing_gr15_scores[
            "original_trust_bonus"
        ] = df_existing_gr15_scores.trust_bonus

        df_apu_scores = pd.DataFrame.from_dict(
            {
                "user_id": [user.id for user in self.users],
                "Score": APU_SCORES_REDUCED,
                "current_stamps": [["Google", "Facebook", "POAP"] for _ in self.users],
                "has_removed_stamps": HAS_REMOVED_STAMPS,
            }
        )

        df_existing_gr15_scores.set_index("user_id", inplace=True)
        df_apu_scores.set_index("user_id", inplace=True)

        df_trust_bonus_calculation = calculate_trust_bonus(
            df_existing_gr15_scores, df_apu_scores
        )

        assert list(df_trust_bonus_calculation.last_apu_score) == list(
            df_apu_scores.Score
        )
        # Users should have reduced trust bonus scores, because they also had stamps removed
        assert (
            list(df_trust_bonus_calculation.trust_bonus) == EXPECTED_REDUCED_TRUST_BONUS
        )

    def test_trust_bonus_to_min_if_all_stamps_removed(self):
        """Test that the trust bonus does shrink for users that have had stamps removed"""

        old_users = [
            User.objects.create(password=CURRENT_PASSWORD, username=f"old_user_{i}")
            for i in range(3)
        ]

        NEW_APU_MEDIAN = 0.35
        NEW_APU_MIN = 0

        users = self.users + old_users

        # This should resulnt in smaller trust bonus being calculated for users at
        # the index: 1, 2, 3, 4 as we reduced their APU and they are below median
        EXPECTED_APU_SCORES = APU_SCORES + [0 for _ in old_users]

        HAS_REMOVED_STAMPS = [
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        # Users with no stamps whould get their score reduced to 0
        EXPECTED_REDUCED_TRUST_BONUS = [
            (
                (i - NEW_APU_MIN)
                / (NEW_APU_MEDIAN - NEW_APU_MIN)
                * (MAX_TRUST_BONUS - MIN_TRUST_BONUS)
                + MIN_TRUST_BONUS
            )
            if i < NEW_APU_MEDIAN
            else 1.5
            for i in APU_SCORES
        ] + [0.5 for _ in old_users]

        # the df_existing_gr15_scores will contain records of older calculation runs
        df_existing_gr15_scores = pd.DataFrame.from_dict(
            {
                "id": [user.id for user in users],
                "user_id": [user.id for user in users],
                "last_apu_score": APU_SCORES + [0.2 for _ in old_users],
                "max_apu_score": APU_SCORES + [0.2 for _ in old_users],
                "trust_bonus": EXPECTED_TRUST_BONUS + [1.2 for _ in old_users],
                "last_apu_calculation_time": [timezone.now() for _ in users],
                "max_apu_calculation_time": [timezone.now() for _ in users],
                "trust_bonus_calculation_time": [timezone.now() for _ in users],
                "stamps": ["" for _ in users],
            }
        )

        df_existing_gr15_scores[
            "original_last_apu_score"
        ] = df_existing_gr15_scores.last_apu_score
        df_existing_gr15_scores[
            "original_trust_bonus"
        ] = df_existing_gr15_scores.trust_bonus

        df_apu_scores = pd.DataFrame.from_dict(
            {
                "user_id": [user.id for user in self.users],
                "Score": APU_SCORES,
                "current_stamps": [["Google", "Facebook", "POAP"] for _ in self.users],
                "has_removed_stamps": HAS_REMOVED_STAMPS,
            }
        )

        df_existing_gr15_scores.set_index("user_id", inplace=True)
        df_apu_scores.set_index("user_id", inplace=True)

        df_trust_bonus_calculation = calculate_trust_bonus(
            df_existing_gr15_scores, df_apu_scores
        )

        assert list(df_trust_bonus_calculation.last_apu_score) == EXPECTED_APU_SCORES

        assert (
            list(df_trust_bonus_calculation.trust_bonus) == EXPECTED_REDUCED_TRUST_BONUS
        )

    def test_trust_bonus_calc_if_all_apus_equal(self):
        """Test the trust bonus calculation if all APUs are equal"""

        EQUAL_APU_SCORES = [0.75 for _ in self.users]

        # Users with no stamps whould get their score reduced to 0
        EXPECTED_TRUST_BONUS_FOR_EQ_APU = [0.5 for _ in self.users]

        # the df_existing_gr15_scores will contain records of older calculation runs
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
                "stamps": [],
            }
        )
        df_existing_gr15_scores[
            "original_last_apu_score"
        ] = df_existing_gr15_scores.last_apu_score
        df_existing_gr15_scores[
            "original_trust_bonus"
        ] = df_existing_gr15_scores.trust_bonus

        df_apu_scores = pd.DataFrame.from_dict(
            {
                "user_id": [user.id for user in self.users],
                "Score": EQUAL_APU_SCORES,
                "current_stamps": [["Google", "Facebook", "POAP"] for _ in self.users],
                "has_removed_stamps": [False for _ in self.users],
            }
        )

        df_existing_gr15_scores.set_index("user_id", inplace=True)
        df_apu_scores.set_index("user_id", inplace=True)

        df_trust_bonus_calculation = calculate_trust_bonus(
            df_existing_gr15_scores, df_apu_scores
        )

        assert list(df_trust_bonus_calculation.last_apu_score) == EQUAL_APU_SCORES

        print("list(df_trust_bonus_calculation.trust_bonus):\n", list(df_trust_bonus_calculation.trust_bonus))
        print("EXPECTED_TRUST_BONUS_FOR_EQ_APU:\n", EXPECTED_TRUST_BONUS_FOR_EQ_APU)

        assert (
            list(df_trust_bonus_calculation.trust_bonus) == EXPECTED_TRUST_BONUS_FOR_EQ_APU
        )
