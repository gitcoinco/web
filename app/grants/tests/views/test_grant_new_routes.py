import json
import pytest

from os.path import dirname, join
from django.test import Client

from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import GrantTypeFactory


@pytest.mark.django_db
class TestNewGrantGetRoute:
    def test_when_not_logged_in_redirects_to_github_for_auth(self):
        client = Client(HTTP_USER_AGENT='chrome')
        response = client.get('/grants/new')
        content = str(response.content)

        assert response.status_code == 200
        assert 'Create a Grant' not in content
        assert 'Please log in before submitting a grant' in content

    def test_when_logged_in_renders_grants_new_template(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        ProfileFactory(user=user, handle='gitcoin')

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.get('/grants/new')

        assert response.status_code == 200
        assert 'Create a Grant' in str(response.content)


@pytest.mark.django_db
class TestNewGrantsPostRoute:
    def test_redirects_to_login_when_not_authenticated(self):
        client = Client(HTTP_USER_AGENT='chrome')
        response = client.post('/grants/new')

        assert response.status_code == 302
        assert "gh-login" in response.url

    def test_requires_a_profile_associated_to_the_logged_in_user(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new')
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: no matching profile found'

    def test_requires_grant_type(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new')
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: grant_type is a mandatory parameter'

    def test_requires_a_title(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', {'grant_type': 'gr12'})
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: title is a mandatory parameter'

    def test_requires_a_description(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', {'grant_type': 'gr12', 'title': 'Test Submission'})
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: description is a mandatory parameter'

    def test_requires_has_external_funding_selection(
        self,
        django_user_model
    ):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')
        grant_data = {
            'grant_type': 'gr12',
            'title': 'Test Submission',
            'description': 'This is a test grant submission',
        }

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', grant_data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: has_external_funding is a mandatory parameter'

    def test_requires_payout_address(
        self,
        django_user_model
    ):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')
        grant_data = {
            'grant_type': 'gr12',
            'title': 'Test Submission',
            'description': 'This is a test grant submission',
            'has_external_funding': 'no',
        }

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', grant_data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: payout_address is a mandatory parameter'

    def test_zcash_addresses_must_be_tranparent_addresses(
        self,
        django_user_model
    ):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')
        grant_data = {
            'grant_type': 'gr12',
            'title': 'Test Submission',
            'description': 'This is a test grant submission',
            'has_external_funding': 'no',
            'zcash_payout_address': '0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c',
        }

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', grant_data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: zcash_payout_address must be a transparent address'

    def test_requires_logo_to_be_an_image(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')

        with open(join(dirname(__file__), 'resources/not_an_image.txt'), 'rb') as logo:
            grant_data = {
                'grant_type': 'gr12',
                'title': 'Test Submission',
                'description': 'This is a test grant submission',
                'has_external_funding': 'no',
                'admin_address': '0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c',
                'logo': logo,
            }

            client = Client(HTTP_USER_AGENT='chrome')
            client.force_login(user)
            response = client.post('/grants/new', grant_data)
            response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: invalid logo file'

    def test_requires_valid_project_twitter_handle(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')
        _grant_type = GrantTypeFactory(name='gr12')
        grant_data = {
            'grant_type': 'gr12',
            'title': 'Test Submission',
            'description': 'This is a test grant submission',
            'has_external_funding': 'no',
            'admin_address': '0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c',
            'handle1': '!',
        }

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', grant_data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: enter a valid project twitter handle e.g @humanfund'

    def test_requires_valid_personal_twitter_handle(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')
        _grant_type = GrantTypeFactory(name='gr12')
        grant_data = {
            'grant_type': 'gr12',
            'title': 'Test Submission',
            'description': 'This is a test grant submission',
            'has_external_funding': 'no',
            'admin_address': '0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c',
            'handle2': '!',
        }

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', grant_data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 400
        assert response_data.get('message') == 'error: enter your twitter handle e.g @georgecostanza'

    def test_creates_new_grant_when_required_fields_submitted(self, django_user_model):
        user = django_user_model.objects.create(username='gitcoin', password='password123')
        _profile = ProfileFactory(user=user, handle='gitcoin')
        _grant_type = GrantTypeFactory(name='gr12')
        grant_data = {
            'grant_type': 'gr12',
            'title': 'Test Submission',
            'description': 'This is a test grant submission',
            'has_external_funding': 'no',
            'admin_address': '0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c',
            'team_members[]': '',
            'tags[]': '',
        }

        client = Client(HTTP_USER_AGENT='chrome')
        client.force_login(user)
        response = client.post('/grants/new', grant_data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data.get('status') == 200
