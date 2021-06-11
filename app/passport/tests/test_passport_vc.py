import json
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from dashboard.models import Profile
from didkit import verifyCredential
from rest_framework import status

CURRENT_USERNAME = "passport"
CURRENT_PASSWORD = "passport"

class PassportVCTest(TestCase):
    """Define tests for passport verifiable credential."""
    def setUp(self):
        self.current_user = User.objects.create(
                password=CURRENT_PASSWORD,
                username=CURRENT_USERNAME)

        Profile.objects.create(
                user=self.current_user,
                data={},
                hide_profile=False,
                handle=CURRENT_USERNAME)

    def test_issue_and_verify_credential(self):
        """ Tests that the issued passport credential verifies """
        self.client.force_login(self.current_user)

        data = {
            "network":"mainnet",
            "coinbase":"0x0000000000000000000000000000000000000000"}

        response = self.client.get(reverse("passport_vc"),
                data,
                HTTP_USER_AGENT="none")

        self.assertTrue(status.is_success(response.status_code))

        vc = response.json()['vc']
        options = {"proofPurpose": "assertionMethod"}
        verifyStr = verifyCredential(
                json.dumps(vc),
                json.dumps(options))

        verify = json.loads(verifyStr)
        self.assertFalse(verify["errors"])

        pass
