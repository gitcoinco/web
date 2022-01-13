import pytest
from django.test import Client


@pytest.mark.django_db
class TestCLRMatchesView:
    def test_requires_login(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')

        client = Client(HTTP_USER_AGENT='chrome')
        response = client.post('/grants/v1/api/clr-matches', {})

        assert response.status_code == 301
