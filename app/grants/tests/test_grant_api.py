import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory
from grants.tests.factories.grant_factory import GrantFactory
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestGrantAPI:
    def test_grant_edit(self, django_user_model):
        user = django_user_model.objects.create(username="gitcoinco", password="password123")
        client = APIClient()
        client.force_login(user)

        grant = GrantFactory()
        profile = ProfileFactory()
        profile.handle = user.username
        user.profile = profile
        user.is_staff = True
        user.save()
        # grant.team_members.set([profile.id])
        grant.save()

        response = client.post(
            f"/grants/v1/api/grant/edit/{grant.id}/",
            {"title": "This is a new title"},
            format="json",
        )
        print(response.json())

        grant.refresh_from_db()

        assert response.status_code == 200
        assert grant.title == "This is a new title"
