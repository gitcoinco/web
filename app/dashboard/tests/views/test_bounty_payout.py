import pytest
from dashboard.tests.factories.bounty_factory import BountyFactory
from dashboard.tests.factories.fulfillment_factory import FulfillmentFactory
from dashboard.tests.factories.profile_factory import ProfileFactory
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestBountyPayout:
    def test_pays_out_bounty(self, django_user_model):
        github_url = {'github_url': 'https://github.com/gitcoinco/web/issues/1'}
        BountyFactory(**github_url)
        user = django_user_model.objects.create(username="gitcoin", password="password123")
        ProfileFactory(user=user)
        fulfillment = FulfillmentFactory()

        client = APIClient()

        client.force_login(user)

        payload = {
            'payout_type': 'fiat',
            'tenant': 'testtenant',
            'amount': '1',
            'token_name': 'ETH',
            'funder_address': '0x0',
            'payout_status': 'pending',
            'funder_identifier': 'test_funder_identifier',
            'payout_tx_id': '0x0',
        }

        response = client.post(f'/api/v1/bounty/payout/{fulfillment.id}', payload)

        assert response.status_code == 200
