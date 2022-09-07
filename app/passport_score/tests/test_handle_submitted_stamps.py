from django.contrib.auth.models import User
from django.utils import timezone

import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.models import GR15TrustScore
from passport_score.utils import handle_submitted_passport, handle_submitted_stamps, load_passport_stamps
from test_plus.test import TestCase

NUM_USERS = 2


CURRENT_PASSWORD = "mimamamemima"

dids = [f"did:for:user:{i}" for i in range(NUM_USERS)]
many_stamps = [
    {
        "credential": {
            "credentialSubject": {
            "hash": f"many_{provider}",
            "provider": provider
            }
    }
    }
    for provider in ["Google", "Facebook", "Twitter", "POAP", "Linkedin"]
]
less_stamps = [
    {
        "credential": {
            "credentialSubject": {
            "hash": f"less_{provider}",
            "provider": provider
            }
    }
    }
    for provider in [
        "Google",
        "Facebook",
    ]
]

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
        assert PassportStamp.objects.filter(passport=self.passport1).count() == len(many_stamps)
        assert PassportStamp.objects.filter(passport=self.passport2).count() == len(less_stamps)
        assert PassportStamp.objects.count() == len(less_stamps) + len(many_stamps)

    def test_handle_user_removes_stamps(self):
        """Test handling user removing stamps"""

        handle_submitted_stamps(self.passport1, self.user1.id, many_stamps)
        handle_submitted_stamps(self.passport1, self.user1.id, less_stamps)

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 0
        assert PassportStamp.objects.filter(passport=self.passport1).count() == len(less_stamps)
        assert PassportStamp.objects.count() == len(less_stamps)

    def test_handle_user_duplicate_stamp(self):
        """Test handling user submitting a stamp that is already linked to another user"""

        handle_submitted_stamps(self.passport1, self.user1.id, many_stamps)
        handle_submitted_stamps(self.passport2, self.user2.id, many_stamps[:1] + less_stamps)

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 1
        user1_gr15_trust_score = GR15TrustScore.objects.get(user_id=self.user1.id)

        dup_hash = many_stamps[0]["credential"]["credentialSubject"]["hash"]
        assert (
            user1_gr15_trust_score.notes[0]["note"]
            == f"Marking as sybil. Duplicate stamp id: {dup_hash}"
        )
        assert user1_gr15_trust_score.is_sybil

        # The "duplicate" stamp has been moved frm user1 to user 2
        assert PassportStamp.objects.filter(passport=self.passport1).count() == len(many_stamps) - 1
        assert PassportStamp.objects.filter(user=self.user1).count() == len(many_stamps) - 1
        assert PassportStamp.objects.filter(passport=self.passport2).count() == len(less_stamps) + 1
        assert PassportStamp.objects.filter(user=self.user2).count() == len(less_stamps) + 1
        assert PassportStamp.objects.count() == len(less_stamps) + len(many_stamps)
