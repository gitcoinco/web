import json

import pytest
from rest_framework.test import APIClient

from dashboard.tests.factories import ProfileFactory

from grants.tests.factories import GrantFactory, CLRMatchFactory


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='gitcoin', password='password123')


@pytest.fixture
def profile(user):
    return ProfileFactory(user=user, handle='gitcoin')


@pytest.fixture
def grant(profile):
    grant = GrantFactory.create(admin_profile=profile)
    CLRMatchFactory(grant=grant)

    return grant


@pytest.mark.django_db
class TestCLRMatchesGetRequestView:
    def test_requires_login(self):
        client = APIClient()
        response = client.get('/grants/v1/api/clr-matches/')

        assert response.status_code == 302

    def test_requires_profile(self, user):
        client = APIClient()
        client.force_login(user=user)

        response = client.get('/grants/v1/api/clr-matches/')
        content = json.loads(response.content)

        assert response.status_code == 404
        assert content.get('message') == 'Profile not found!'

    def test_response_data_is_empty_when_user_does_not_have_any_grants(self, profile):
        client = APIClient()
        client.force_login(user=profile.user)

        response = client.get('/grants/v1/api/clr-matches/')
        content = json.loads(response.content)

        assert response.status_code == 200
        assert content == []

    def test_response_data_includes_grants_and_clr_matches(self, grant):
        expected_keys = ['id', 'title', 'logo_url', 'details_url', 'admin_address', 'clr_matches']
        client = APIClient()
        client.force_login(user=grant.admin_profile.user)

        response = client.get('/grants/v1/api/clr-matches/')
        content = json.loads(response.content)

        assert response.status_code == 200
        assert len(content) == 1
        assert sorted(content[0].keys()) == sorted(expected_keys)
