import pytest
from dashboard.tests.factories import BountyFactory
from rest_framework.test import APIClient


class TestBountyAPI:
    def test_retrieves_activities(self, django_user_model):
        github_url = {'github_url': 'https://github.com/gitcoinco/web/issues/1'}
        BountyFactory(**github_url)
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        client = APIClient()

        client.force_login(user)
        response = client.get('/actions/api/v0.1/bounty/', github_url, format='json')

        assert response.status_code == 200
