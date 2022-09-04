from django.contrib.auth.models import User
from django.utils import timezone

import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.management.commands.test_compute_gr15_trust_bonus import (
    get_new_trust_bonus, load_passport_stamps, save_gr15_trustbonus_records,
)
from passport_score.models import GR15TrustScore
from test_plus.test import TestCase

NUM_USERS = 10

CURRENT_PASSWORD = "mimamamemima"
usernames = [f"test_user_{i}" for i in range(NUM_USERS)]
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

    def ttttest_trust_bonus_increases(self):
        """Test cunputing the GR15TrustScore the first time (no other records in GR15TrustScore)
        and that increses ..."""

        create_stamps(
            [
                ("test_user_1", ["Google"]),
                ("test_user_2", ["Google"]),
                ("test_user_3", ["Google"]),
                ("test_user_4", ["Google"]),
                ("test_user_5", ["Google"]),
                ("test_user_6", ["Google"]),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)

        initial_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        PassportStamp.objects.all().delete()
        create_stamps(
            [
                ("test_user_1", ["Google"]),
                ("test_user_2", ["Google"]),
                ("test_user_3", ["Google"]),
                ("test_user_4", ["Facebook"]),
                ("test_user_5", ["Facebook"]),
                ("test_user_6", ["Twitter"]),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)

        second_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        is_second_trust_bonus_larger = [
            tb1 < tb2
            for tb1, tb2 in zip(initial_gr15_trust_bonus, second_gr15_trust_bonus)
        ]
        print("initial_gr15_trust_bonus", initial_gr15_trust_bonus)
        print("second_gr15_trust_bonus", second_gr15_trust_bonus)
        assert len(initial_gr15_trust_bonus) == len(second_gr15_trust_bonus)
        assert all(is_second_trust_bonus_larger)

    def test_trust_bonus_will_not_shrink(self):
        """Test that the trust bonus will not shrink even if accoring to the formula based on APU it should"""

        create_stamps(
            [
                (
                    "test_user_1",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                        "Poh",
                    ],
                ),
                (
                    "test_user_2",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                    ],
                ),
                ("test_user_3", ["Facebook", "Twitter", "POAP", "Discord", "Linkedin"]),
                (
                    "test_user_4",
                    [
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                    ],
                ),
                ("test_user_5", ["Facebook", "Twitter", "POAP"]),
                ("test_user_6", ["Facebook", "Twitter"]),
            ]
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)

        initial_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        PassportStamp.objects.all().delete()
        create_stamps(
            [
                (
                    "test_user_1",
                    [
                        "Google",
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                        "Poh",
                    ],
                ),
                (
                    "test_user_2",
                    [
                        "Google",
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                        "Linkedin",
                        "Ens",
                    ],
                ),
                (
                    "test_user_3",
                    ["Google", "Facebook", "Twitter", "POAP", "Discord", "Linkedin"],
                ),
                (
                    "test_user_4",
                    [
                        "Google",
                        "Facebook",
                        "Twitter",
                        "POAP",
                        "Discord",
                    ],
                ),
                ("test_user_5", ["Google", "Facebook", "Twitter", "POAP"]),
                ("test_user_6", ["Google", "Facebook", "Twitter"]),
            ],
        )

        df_trust_bonus = get_new_trust_bonus()
        save_gr15_trustbonus_records(df_trust_bonus)

        second_gr15_trust_bonus = [
            gr15.trust_bonus for gr15 in GR15TrustScore.objects.order_by("user_id")
        ]

        print("initial_gr15_trust_bonus", initial_gr15_trust_bonus)
        print("second_gr15_trust_bonus", second_gr15_trust_bonus)
        assert initial_gr15_trust_bonus == second_gr15_trust_bonus
        assert False
