import pytest
from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import GrantFactory
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestGrantAPI:
    def test_grant_edit(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        client = APIClient()
        client.force_login(user)

        grant = GrantFactory()
        ProfileFactory(user=user)
        user.is_staff = True
        user.save()

        response = client.post(
            f"/grants/v1/api/grant/edit/{grant.id}/",
            {
                "title": "This is a new title",
                "description": grant.description,
                "has_external_funding": "yes",
                "eth_payout_address": grant.admin_address,
            },
        )

        grant.refresh_from_db()

        assert response.status_code == 200
        assert grant.title == "This is a new title"
