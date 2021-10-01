from django.test import Client

import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory


@pytest.mark.django_db
class TestProfileTabProjectCreation:
    def test_project_creation_fails_when_url_does_not_start_with_http(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        project_data = dict(project_title="My New Project", URL="gitcoin.co")
        ProfileFactory(user=user, handle="gitcoin")

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/gitcoin/portfolio', project_data)
        messages = [m.messages for m in response.context['messages']]

        assert response.status_code == 200
        assert "Invalid link." in messages
        assert "Portfolio Item added." not in messages

    def test_project_creation_fails_when_url_is_empty(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        project_data = dict(project_title="My New Project", URL="")
        ProfileFactory(user=user, handle="gitcoin")

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/gitcoin/portfolio', project_data)
        messages = [m.message for m in response.context['messages']]

        assert response.status_code == 200
        assert "Please enter some tags." in messages
        assert "Portfolio Item added." not in messages
