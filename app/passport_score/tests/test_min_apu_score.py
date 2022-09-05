from django.contrib.auth.models import User
from django.utils import timezone

import pandas as pd
import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.gr15_scorer import compute_apu_scores
from passport_score.utils import calculate_trust_bonus, get_min_apu_for_user, load_passport_stamps
from test_plus.test import TestCase

CURRENT_USERNAME = "bot_dude"
CURRENT_PASSWORD = "mimamamemima"


EXPECTED_APU_SCORES = [1 / len(providers), 2 / len(providers), 3 / len(providers)]

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
    for i in EXPECTED_APU_SCORES
]
NUM_USERS = len(EXPECTED_APU_SCORES)

USER_STAMPS = [providers[:i] for i, _ in enumerate(EXPECTED_APU_SCORES, 1)]


def create_stamps(stamps_list):
    for username, providers in stamps_list:
        passport = Passport.objects.get(user__username=username)
        for provider in providers:
            PassportStamp.objects.create(
                passport=passport,
                user=passport.user,
                stamp_id=f"{passport.user.id}_{passport.id}_{provider}",
                stamp_provider=provider,
                stamp_credential={"type": "test"},
            )


@pytest.mark.django_db
class TestTrustBonusCalculation(TestCase):
    """Test trust bonus alculation."""

    def setUp(self):
        self.users = [
            User.objects.create(password=CURRENT_PASSWORD, username=f"user_{i}")
            for i in range(NUM_USERS)
        ]

        self.passports = [
            Passport.objects.create(
                user=user, did=user.username, passport={"type": user.username}
            )
            for user in self.users
        ]

    def test_dummy(self):
        """Calculating the trust bonus when GR15TrustScore is empty"""

        print(self.users)
        create_stamps(
            [
                (
                    "user_0",
                    [
                        "Facebook",
                    ],
                ),
                (
                    "user_1",
                    ["Facebook", "Google"],
                ),
                (
                    "user_2",
                    ["Facebook", "Google", "Twitter"],
                ),
            ]
        )

        (
            prepared_df,
            stamp_fields,
            grouping_fields,
            grouping_fields_1,
        ) = load_passport_stamps()

        df_apu_scores = compute_apu_scores(
            prepared_df, stamp_fields, grouping_fields, grouping_fields_1
        )

        print(df_apu_scores)

        assert EXPECTED_APU_SCORES == list(df_apu_scores.Score)

        min_apu_scores = [
            get_min_apu_for_user(self.users[0].id),
            get_min_apu_for_user(self.users[1].id),
            get_min_apu_for_user(self.users[2].id),
        ]
        assert EXPECTED_APU_SCORES == min_apu_scores
