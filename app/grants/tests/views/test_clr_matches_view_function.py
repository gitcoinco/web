import json

import pytest
from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import CLRMatchFactory, GrantFactory, GrantPayoutFactory
from rest_framework.test import APIClient


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='gitcoin', password='password123')


@pytest.fixture
def profile(user):
    return ProfileFactory(user=user, handle='gitcoin')


@pytest.fixture
def grant(profile):
    grnt = GrantFactory.create(admin_profile=profile)
    grant_payout = GrantPayoutFactory()
    CLRMatchFactory(grant=grnt, grant_payout=grant_payout)

    return grnt


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


@pytest.mark.django_db
class TestCLRMatchesPostRequestView:
    def test_requires_login(self):
        client = APIClient()
        response = client.post('/grants/v1/api/clr-matches/')

        assert response.status_code == 302

    def test_requires_profile(self, user):
        client = APIClient()
        client.force_login(user=user)

        response = client.post('/grants/v1/api/clr-matches/')
        content = json.loads(response.content)

        assert response.status_code == 404
        assert content.get('message') == 'Profile not found!'

    def test_requires_pk_field(self, profile):
        client = APIClient()
        client.force_login(user=profile.user)

        response = client.post('/grants/v1/api/clr-matches/', {}, format='json')
        content = json.loads(response.content)

        assert response.status_code == 400
        assert content.get('message') == 'pk field is required!'

    def test_requires_claim_tx_field(self, profile):
        client = APIClient()
        client.force_login(user=profile.user)

        response = client.post('/grants/v1/api/clr-matches/', {'pk': 1}, format='json')
        content = json.loads(response.content)

        assert response.status_code == 400
        assert content.get('message') == 'claim_tx field is required!'

    def test_404_when_clr_match_not_found(self, profile):
        client = APIClient()
        client.force_login(user=profile.user)
        request_data = {'pk': 1, 'claim_tx': 'abd123'}

        response = client.post('/grants/v1/api/clr-matches/', request_data, format='json')
        content = json.loads(response.content)

        assert response.status_code == 404
        assert content.get('message') == 'CLR Match not found!'

    def test_updates_clr_match(self, grant):
        match = grant.clr_matches.first()
        existing_claim_tx = match.claim_tx
        request_data = {
            'pk': match.pk,
            'claim_tx': 'abc123'
        }

        client = APIClient()
        client.force_login(user=grant.admin_profile.user)

        response = client.post('/grants/v1/api/clr-matches/', request_data, format='json')
        match.refresh_from_db()

        assert response.status_code == 200
        assert match.claim_tx != existing_claim_tx
        assert match.claim_tx == 'abc123'
