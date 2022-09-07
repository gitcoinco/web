from decimal import Decimal

from django.contrib.auth.models import User
from django.utils import timezone

import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.models import GR15TrustScore
from passport_score.utils import (
    MAX_TRUST_BONUS, MIN_TRUST_BONUS, get_apu_median, get_apu_min, handle_submitted_passport, handle_submitted_stamps,
    load_passport_stamps,
)
from test_plus.test import TestCase

NUM_USERS = 2


CURRENT_PASSWORD = "mimamamemima"

dids = [f"did:for:user:{i}" for i in range(NUM_USERS)]
many_stamps = [
    {
        "credential": {
            "credentialSubject": {"hash": f"many_{provider}", "provider": provider}
        }
    }
    for provider in ["Google", "Facebook", "Twitter", "POAP", "Linkedin"]
]
less_stamps = [
    {
        "credential": {
            "credentialSubject": {"hash": f"less_{provider}", "provider": provider}
        }
    }
    for provider in [
        "Google",
        "Facebook",
    ]
]


def decimal_equal(d1, d2):
    """Determine if 2 numbers are equal as decimals"""
    d1_str = str(Decimal(d1))
    d2_str = str(Decimal(d2))
    l = min(len(d1_str), len(d2_str))

    return l > 0 and d1_str[:l] == d2_str[:l]


@pytest.mark.django_db
class TestHandleSubmittedPassport(TestCase):
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
        self.did1 = dids[0]
        self.did2 = dids[1]
        self.passport1 = self.passports[0]
        self.passport2 = self.passports[1]

    def test_handle_valid_stamps(self):
        """Test handling 2 valid submissions"""

        handle_submitted_stamps(self.passport1, self.user1.id, many_stamps)
        handle_submitted_stamps(self.passport2, self.user2.id, less_stamps)

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 0
        assert Passport.objects.count() == 2
        assert PassportStamp.objects.filter(passport=self.passport1).count() == len(
            many_stamps
        )
        assert PassportStamp.objects.filter(passport=self.passport2).count() == len(
            less_stamps
        )
        assert PassportStamp.objects.count() == len(less_stamps) + len(many_stamps)

    def test_handle_user_removes_stamps(self):
        """Test handling user removing stamps"""

        handle_submitted_stamps(self.passport1, self.user1.id, many_stamps)
        handle_submitted_stamps(self.passport1, self.user1.id, less_stamps)

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 0
        assert PassportStamp.objects.filter(passport=self.passport1).count() == len(
            less_stamps
        )
        assert PassportStamp.objects.count() == len(less_stamps)

    def test_handle_user_duplicate_stamp(self):
        """Test handling user submitting a stamp that is already linked to another user"""

        handle_submitted_stamps(self.passport1, self.user1.id, many_stamps)
        handle_submitted_stamps(
            self.passport2, self.user2.id, many_stamps[:1] + less_stamps
        )

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 1
        user1_gr15_trust_score = GR15TrustScore.objects.get(user_id=self.user1.id)

        dup_hash = many_stamps[0]["credential"]["credentialSubject"]["hash"]
        assert (
            user1_gr15_trust_score.notes[0]["note"]
            == f"Marking as sybil. Duplicate stamp id: {dup_hash}"
        )
        assert user1_gr15_trust_score.is_sybil
        expected_apu_score = (len(many_stamps) - 1) / len(providers)
        apu_median = get_apu_median()
        apu_min = get_apu_min()
        expected_trust_bonus = Decimal("1.50000000000000000000000000000000")

        if expected_apu_score < apu_median:
            expected_trust_bonus = (expected_apu_score - apu_min) / (
                apu_median - apu_min
            ) * (Decimal(MAX_TRUST_BONUS) - Decimal(MIN_TRUST_BONUS)) + Decimal(
                MIN_TRUST_BONUS
            )

        assert decimal_equal(expected_apu_score, user1_gr15_trust_score.last_apu_score)
        assert decimal_equal(expected_trust_bonus, user1_gr15_trust_score.trust_bonus)

        # The "duplicate" stamp has been moved frm user1 to user 2
        assert (
            PassportStamp.objects.filter(passport=self.passport1).count()
            == len(many_stamps) - 1
        )
        assert (
            PassportStamp.objects.filter(user=self.user1).count()
            == len(many_stamps) - 1
        )
        assert (
            PassportStamp.objects.filter(passport=self.passport2).count()
            == len(less_stamps) + 1
        )
        assert (
            PassportStamp.objects.filter(user=self.user2).count()
            == len(less_stamps) + 1
        )
        assert PassportStamp.objects.count() == len(less_stamps) + len(many_stamps)
