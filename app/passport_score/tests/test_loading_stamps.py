from django.contrib.auth.models import User
from django.utils import timezone

import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.models import GR15TrustScore
from passport_score.utils import load_passport_stamps
from test_plus.test import TestCase

NUM_USERS = 10

CURRENT_USERNAME = "bot_dude"
CURRENT_PASSWORD = "mimamamemima"

user_providers_lists = [
    [
        "Google",
    ],
    [
        "Google",
        "Facebook",
    ],
    ["Google", "Facebook", "POAP"],
]


@pytest.mark.django_db
class TestLoadingStamps(TestCase):
    """Test loading stamps for APU calculation."""

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

        self.user1 = self.users[0]
        self.user2 = self.users[1]
        self.user3 = self.users[2]

        for idx, user_providers in enumerate(user_providers_lists):
            for provider in user_providers:
                PassportStamp(
                    passport=self.passports[idx],
                    user=self.passports[idx].user,
                    stamp_id=f"stamp_{self.passports[idx].id}_{provider}",
                    stamp_provider=provider,
                ).save()

    def test_loading_stamps(self):
        """Test loading stamps when no entries exist in GR15TrustScore"""

        (
            prepared_df,
            _providers,
            grouping_fields,
            grouping_fields_1,
        ) = load_passport_stamps()

        assert prepared_df.shape == (3, 64)

        expected_columns = providers + [
            "user_id",
            "is_stamp_preserved",
            "stamp_provider",
        ]
        expected_columns.sort()
        received_columns = sorted(prepared_df.columns)

        assert expected_columns == received_columns

        prepared_df.set_index("user_id", inplace=True)

        assert list(prepared_df["is_stamp_preserved"]) == [1, 1, 1]
        assert list(prepared_df["Google"]) == [1, 1, 1]
        assert list(prepared_df["Facebook"]) == [0, 1, 1]
        assert list(prepared_df["POAP"]) == [0, 0, 1]

        for provider in set(providers).difference(["Google", "Facebook", "POAP"]):
            assert list(prepared_df[provider]) == [0, 0, 0]

        assert _providers == providers
        assert grouping_fields == ["stamp_provider", "is_stamp_preserved"]
        assert grouping_fields_1 == ["user_id", "stamp_provider", "is_stamp_preserved"]

    def test_loading_stamps_removed_from_gr15_trust_score(self):
        """Test loading stamps when some stamps have been removed from GR15TrustScore"""

        # Users 2 and 3 will have stamps in GR15TrustScore that are not in PassportStamp
        for i in range(3):
            GR15TrustScore.objects.create(
                user=self.users[i],
                last_apu_score=0.2,
                max_apu_score=0.3,
                trust_bonus=1,
                last_apu_calculation_time=timezone.now(),
                max_apu_calculation_time=timezone.now(),
                trust_bonus_calculation_time=timezone.now(),
                stamps=["Google"] if i == 0 else ["Google", "Twitter"],
                is_sybil=False,
                notes=[],
            )

        (
            prepared_df,
            _providers,
            grouping_fields,
            grouping_fields_1,
        ) = load_passport_stamps()

        print(prepared_df)
        assert list(prepared_df["is_stamp_preserved"]) == [1, 0, 0]

    def test_loading_stamps_all_stamps_removed_from_gr15_trust_score(self):
        """Test loading stamps when all stamps have been removed for a user that has an entry in GR15TrustScore"""

        # Users 2 and 3 will have all stamps removed from PassportStamp
        self.passports[1].delete()
        self.passports[2].delete()
        for i in range(3):
            GR15TrustScore.objects.create(
                user=self.users[i],
                last_apu_score=0.2,
                max_apu_score=0.3,
                trust_bonus=1,
                last_apu_calculation_time=timezone.now(),
                max_apu_calculation_time=timezone.now(),
                trust_bonus_calculation_time=timezone.now(),
                stamps=["Google"] if i == 0 else [],
                is_sybil=False,
                notes=[],
            )

        (
            prepared_df,
            _providers,
            grouping_fields,
            grouping_fields_1,
        ) = load_passport_stamps()

        print(prepared_df)
        # The resulting dataset should not contain rows for the users with no more stamps
        assert list(prepared_df["is_stamp_preserved"]) == [1]
