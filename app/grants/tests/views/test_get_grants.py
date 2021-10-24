from datetime import datetime

from django.test import Client

import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory
from grants.tests.models.factories.grant_factory import GrantFactory


@pytest.fixture()
def grants():
    profile = ProfileFactory()
    return GrantFactory.create_batch(5, last_update=datetime.now(), admin_profile=profile)

@pytest.mark.django_db
class TestGetGrantsNotAuthenticated():
    def test_without_grants(self):
        client = Client(HTTP_USER_AGENT='chrome')
        response = client.get('/grants/cards_info')

        assert response.status_code == 200
        assert len(response.json()['grants']) == 0

    def test_with_grants_created(self, grants):
        client = Client(HTTP_USER_AGENT='chrome')
        response = client.get('/grants/cards_info')

        assert response.status_code == 200
        assert len(response.json()['grants']) == 5

