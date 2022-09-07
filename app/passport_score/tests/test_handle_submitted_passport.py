from django.contrib.auth.models import User
from django.utils import timezone

import pytest
from dashboard.models import Passport, PassportStamp
from passport_score.gr15_providers import providers
from passport_score.models import GR15TrustScore
from passport_score.utils import handle_submitted_passport, load_passport_stamps
from test_plus.test import TestCase

NUM_USERS = 2


CURRENT_PASSWORD = "mimamamemima"

dids = [f"did:for:user:{i}" for i in range(NUM_USERS)]
passports = [
    {"stamps": [{"provider": "Provider1"}]},
    {"stamps": [{"provider": "Provider2"}]},
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
        self.passport1 = passports[0]
        self.passport2 = passports[1]

    def test_handle_valid_passport(self):
        """Test handling 2 valid submissions"""

        handle_submitted_passport(self.user1.id, self.did1, self.passport1)

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 0
        assert Passport.objects.count() == 2
        assert Passport.objects.filter(user_id=self.user1.id).count() == 1
        assert Passport.objects.filter(user_id=self.user2.id).count() == 1

    def test_handle_duplicate_did(self):
        """
        Test handling 2 submissions with the same did
        - the first user is marked as sybil.
        - the first users passport is deleted (including all his stamps)
        - the first user gets:
            - is_sybil -> True
            - last_apu_score -> 0
            - trust_bonus -> 0
        """

        handle_submitted_passport(self.user1.id, self.did1, self.passport1)
        passport1 = Passport.objects.get(user_id=self.user1.id)
        for provider in ["Google", "Facebook", "POAP"]:
            PassportStamp(
                passport=passport1,
                user=passport1.user,
                stamp_id=f"stamp_{passport1.user_id}_{provider}",
                stamp_provider=provider,
            ).save()

        # Ensure stamps where saved
        assert PassportStamp.objects.filter(user_id=self.user1.id).count() == 3

        handle_submitted_passport(self.user2.id, self.did1, self.passport1)

        # Because of duplicate did, we expect user_1 user to have been flagged as sybil
        assert GR15TrustScore.objects.count() == 1

        user1_gr15_trust_score = GR15TrustScore.objects.get(user_id=self.user1.id)
        assert (
            user1_gr15_trust_score.notes[0]["note"]
            == f"Marking as sybil. Duplicate did: {self.did1}"
        )
        assert user1_gr15_trust_score.is_sybil
        assert user1_gr15_trust_score.last_apu_score == 0
        assert user1_gr15_trust_score.trust_bonus == 0

        # Also check that the 1st users passport was deleted
        assert Passport.objects.count() == 1
        assert Passport.objects.filter(user_id=self.user1.id).count() == 0
        assert PassportStamp.objects.filter(user_id=self.user1.id).count() == 0
        assert Passport.objects.filter(user_id=self.user2.id).count() == 1

    def test_handle_user_changes_did(self):
        """
        Test te case when user changes did:
        - first passport should be deleted
        - all stamps for 1st passport should be deleted
        """

        handle_submitted_passport(self.user1.id, self.did1, self.passport1)
        passport1 = Passport.objects.get(user_id=self.user1.id)
        for provider in ["Google", "Facebook", "POAP"]:
            PassportStamp(
                passport=passport1,
                user=passport1.user,
                stamp_id=f"stamp_{passport1.user_id}_{provider}",
                stamp_provider=provider,
            ).save()

        # Ensure passport & stamps where saved
        assert PassportStamp.objects.filter(user_id=self.user1.id).count() == 3
        assert Passport.objects.filter(did=self.did1).count() == 1

        # Now change the did for the user
        handle_submitted_passport(self.user1.id, self.did2, self.passport2)

        # First passport should have been deleted ...
        assert Passport.objects.filter(pk=passport1.pk).count() == 0

        # Stamps should have been deleted
        assert PassportStamp.objects.count() == 0

        # Ensure new passport was saved
        assert Passport.objects.filter(did=self.did2).count() == 1

        # Both passport submissions are correct we expect no entry in GR15TrustScore for now
        assert GR15TrustScore.objects.count() == 0
