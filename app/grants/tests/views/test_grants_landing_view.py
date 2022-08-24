import os

from django.core.files.images import ImageFile
from django.test.client import Client

import pytest
from grants.tests.factories import GrantBrandingRoutingPolicyFactory


@pytest.mark.django_db
class TestGrantLandingBrandingPolicy:

    def test_grant_bg_defaults_to_none(self):
        client = Client(HTTP_USER_AGENT='chrome')

        response = client.get('/grants/')
        grant_bg = response.context['grant_bg']

        assert response.status_code == 200
        assert grant_bg is None

    def test_grant_bg_when_only_one_policy_exists(self):
        policy = GrantBrandingRoutingPolicyFactory()

        client = Client(HTTP_USER_AGENT='chrome')

        response = client.get('/grants/')
        grant_bg = response.context['grant_bg']

        assert grant_bg['url_pattern'] == policy.url_pattern
