import pytest

from django.test import Client

from dashboard.tests.factories import ProfileFactory


@pytest.mark.django_db
class TestNewGrantGetRoute:
    def test_when_not_logged_in_redirects_to_github_for_auth(self):
        client = Client(HTTP_USER_AGENT='chrome')
        response = client.get('/grants/new')

        assert response.status_code == 302
        assert 'gh-login' in response.url

    def test_when_logged_in_renders_grants_new_template(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        ProfileFactory(user=user, handle='gitcoin')

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)

        response = client.get('/grants/new')
        templates = [t.name for t in response.templates]

        assert response.status_code == 200
        assert 'grants/_new.html' in templates




