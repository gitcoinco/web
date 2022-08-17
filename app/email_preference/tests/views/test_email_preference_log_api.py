import json
from django.urls import reverse
from rest_framework.test import APIClient

from email_preference.models import EmailPreferenceLog


class TestEmailPreference:

    def test_email_preference_log(self, django_user_model):

        # test user needs authentication
        client = APIClient()

        response = client.post(reverse('email_preference_log'), format='json')
        assert response.status_code == 401
        assert json.loads(response.content) == {
            'error': 'You must be authenticated'
        }

        # test logs are added to db
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        client.force_login(user=user)
        response = client.post(reverse('email_preference_log'), {
            'test': 'test'
        }, format='json')
        assert response.status_code == 200
        assert json.loads(response.content) == {
            'success': True,
            'msg': 'Data saved'
        }
        email_preference = EmailPreferenceLog.objects.first()
        assert email_preference.event_data == {'test': 'test'}
        assert email_preference.destination == 'hubspot'
        assert not email_preference.processed_at
