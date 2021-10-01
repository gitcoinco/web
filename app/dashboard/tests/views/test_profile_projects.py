from django.test import Client

import pytest
from dashboard.models import PortfolioItem
from dashboard.tests.factories.profile_factory import ProfileFactory


class TestProfileTabProjectCreation:
    def test_project_creation_fails_when_url_does_not_start_with_http(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        project_data = dict(project_title="My New Project", URL="gitcoin.co", tags="")
        ProfileFactory(user=user, handle="gitcoin", hide_profile=False)

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/gitcoin/portfolio', project_data)
        messages = [m.message for m in response.context['messages']]

        assert response.status_code == 200
        assert "Invalid link." in messages
        assert "Portfolio Item added." not in messages

    def test_project_creation_fails_when_not_logged_in(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        project_data = dict(project_title="My New Project", URL="https://gitcoin.co", tags="")
        ProfileFactory(user=user, handle="gitcoin", hide_profile=False)

        client = Client(HTTP_USER_AGENT='chrome')
        response = client.post('/gitcoin/portfolio', project_data)
        messages = [m.message for m in response.context['messages']]

        assert response.status_code == 200
        assert "Not Authorized" in messages
        assert "Portfolio Item added." not in messages

    def test_project_created(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        project_data = dict(project_title="My New Project", URL="http://gitcoin.co", tags="")
        ProfileFactory(user=user, handle="gitcoin", hide_profile=False)

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/gitcoin/portfolio', project_data)
        messages = [m.message for m in response.context['messages']]

        assert response.status_code == 200
        assert "Portfolio Item added." in messages

    @pytest.mark.django_db(transaction=True)
    def test_project_creation_fails_when_project_already_exists(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        project_data = dict(project_title="My New Project", URL="http://gitcoin.co", tags="")
        profile = ProfileFactory(user=user, handle="gitcoin", hide_profile=False)
        PortfolioItem.objects.create(
            profile=profile,
            title=project_data['project_title'],
            link=project_data['URL'],
            tags=[]
        )

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)

        response = client.post('/gitcoin/portfolio', project_data)
        messages = [m.message for m in response.context['messages']]

        assert response.status_code == 200
        assert "Portfolio Already Exists." in messages
