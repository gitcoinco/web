from django.contrib.auth.models import User

import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.management.commands.test_compute_gr15_trust_bonus import (
    get_apu_median, get_new_trust_bonus, save_gr15_trustbonus_records,
)
from passport_score.models import GR15TrustScore
from test_plus.test import TestCase

NUM_USERS = 10

CURRENT_PASSWORD = "mimamamemima"
usernames = [f"test_user_{i}" for i in range(NUM_USERS)]


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
class TestGr15TrustBonusIntegration(TestCase):
    """Test integration of trust bonus calculation."""

    def setUp(self):
        self.users = [
            User.objects.create(password=CURRENT_PASSWORD, username=username)
            for username in usernames
        ]

        self.passports = [
            Passport.objects.create(
                user=user, did=user.username, passport={"type": user.username}
            )
            for user in self.users
        ]

    def test_trust_bonus_increases(self):
        """Test cunputing the GR15TrustScore the first time (no other records in GR15TrustScore)
        and that increses ..."""

        # Create stamps for a smaller APU median
        create_stamps(
            [
                (
                    "test_user_0",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                        "Google",
                    ],
                ),
                (
                    "test_user_1",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                    ],
                ),
                ("test_user_2", ["Facebook", "Twitter", "POAP", "Discord", "Linkedin"]),
                (
                    "test_user_3",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                    ],
                ),
                (
                    "test_user_4",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                    ],
                ),
                ("test_user_5", providers),
                ("test_user_6", providers),
                ("test_user_7", providers),
                ("test_user_8", providers),
                ("test_user_9", providers),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)
        initial_apu_score_median = get_apu_median()

        initial_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        PassportStamp.objects.all().delete()
        create_stamps(
            [
                (
                    "test_user_0",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                        "Google",
                    ],
                ),
                (
                    "test_user_1",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                    ],
                ),
                ("test_user_2", ["Facebook", "Twitter", "POAP", "Discord", "Linkedin"]),
                (
                    "test_user_3",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                    ],
                ),
                (
                    "test_user_4",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                    ],
                ),
                ("test_user_5", providers[: int(len(providers) / 2)]),
                ("test_user_6", providers[: int(len(providers) / 2)]),
                ("test_user_7", providers[: int(len(providers) / 2)]),
                ("test_user_8", providers[: int(len(providers) / 2)]),
                ("test_user_9", providers[: int(len(providers) / 2)]),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)
        second_apu_score_median = get_apu_median()

        second_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        assert len(initial_gr15_trust_bonus) == len(second_gr15_trust_bonus)

        # the median should have decrease (as test_user_5 .. test_user_9 have removed stamps)
        assert initial_apu_score_median > second_apu_score_median

        #  test_user_5 .. test_user_9 will still have 1.5 trust bonus (there are still above median)
        is_trust_bonus_preserved = [
            tb1 == tb2
            for tb1, tb2 in zip(
                initial_gr15_trust_bonus[5:], second_gr15_trust_bonus[5:]
            )
        ]
        assert all(is_trust_bonus_preserved)

        #  test_user_0 .. test_user_3 will have larger trust_bonus. They have the same number of stamps but the apu median
        # got lower
        is_trust_bonus_larger = [
            tb1 < tb2
            for tb1, tb2 in zip(
                initial_gr15_trust_bonus[:4], second_gr15_trust_bonus[:4]
            )
        ]
        assert all(is_trust_bonus_larger)

        #  test_user_4 has the same 0.5, as this is the minimum
        assert initial_gr15_trust_bonus[4] == second_gr15_trust_bonus[4]


    def test_trust_bonus_will_not_shrink(self):
        """Test that the trust bonus will not shrink even if accoring to the formula based on APU it should"""

        # Create stamps for a smaller APU median
        create_stamps(
            [
                (
                    "test_user_0",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                        "Google",
                    ],
                ),
                (
                    "test_user_1",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                    ],
                ),
                ("test_user_2", ["Facebook", "Twitter", "POAP", "Discord", "Linkedin"]),
                (
                    "test_user_3",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                    ],
                ),
                (
                    "test_user_4",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                    ],
                ),
                ("test_user_5", providers[: int(len(providers) / 2)]),
                ("test_user_6", providers[: int(len(providers) / 2)]),
                ("test_user_7", providers[: int(len(providers) / 2)]),
                ("test_user_8", providers[: int(len(providers) / 2)]),
                ("test_user_9", providers[: int(len(providers) / 2)]),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)
        initial_apu_score_median = get_apu_median()

        initial_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        # Create stamps for a larger APU median => according to the formula, user with
        # the same APU score should result in a lower trust bonus (test_user_0 .. test_user_4)
        # However we do not decrease the trust bonus that we record for users. So we verify that this is true
        PassportStamp.objects.all().delete()
        create_stamps(
            [
                (
                    "test_user_0",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                        "Google",
                    ],
                ),
                (
                    "test_user_1",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                    ],
                ),
                ("test_user_2", ["Facebook", "Twitter", "POAP", "Discord", "Linkedin"]),
                (
                    "test_user_3",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                    ],
                ),
                (
                    "test_user_4",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                    ],
                ),
                ("test_user_5", providers),
                ("test_user_6", providers),
                ("test_user_7", providers),
                ("test_user_8", providers),
                ("test_user_9", providers),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)

        second_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]
        second_apu_score_median = get_apu_median()

        # We expect the initial APU score to be smaller (as test_user_1) had only half of the stamps
        assert initial_apu_score_median < second_apu_score_median

        # Even though he median has increased, the trust bonus for the first users should stay the same
        # as we do not decrease it ...
        assert initial_gr15_trust_bonus == second_gr15_trust_bonus
