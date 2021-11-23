import os

import pytest

from django.test.client import Client
from django.core.files.images import ImageFile

from grants.tests.models.factories.grant_branding_routing_policy_factory import GrantBrandingRoutingPolicyFactory


@pytest.mark.django_db
class TestGrantLandingBrandingPolicy:

    def test_grant_bg_defaults_to_none(self):
        client = Client(HTTP_USER_AGENT='chrome')

        response = client.get('/grants/')
        grant_bg = response.context['grant_bg']

        assert response.status_code == 200
        assert grant_bg is None

    def test_grant_bg_when_only_one_policy_exists(self):
        with open(f'{os.path.dirname(__file__)}/../images/gr-12.png', 'rb') as img:
            policy = GrantBrandingRoutingPolicyFactory(main_round_banner=ImageFile(img))

        client = Client(HTTP_USER_AGENT='chrome')

        response = client.get('/grants/')
        grant_bg = response.context['grant_bg']

        assert grant_bg['url_pattern'] == policy.url_pattern
        assert grant_bg['banner_image'] == ''
        assert grant_bg['background_image'] == ''
        assert grant_bg['inline_css'] is policy.inline_css
        assert 'gr-12.png' in grant_bg['main_round_banner']

    def test_grant_bg_prioritization(self):
        with open(f'{os.path.dirname(__file__)}/../images/gr-12.png', 'rb') as img:
            GrantBrandingRoutingPolicyFactory(main_round_banner=ImageFile(img))

        with open(f'{os.path.dirname(__file__)}/../images/gr-13.png', 'rb') as img:
            GrantBrandingRoutingPolicyFactory(main_round_banner=ImageFile(img), priority=2)

        client = Client(HTTP_USER_AGENT='chrome')

        response = client.get('/grants/')
        grant_bg = response.context['grant_bg']

        assert 'gr-13.png' in grant_bg['main_round_banner']



