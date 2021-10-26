import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory
from dashboard.tests.factories.bounty_factory import BountyFactory
from dashboard.tests.factories.fulfillment_factory import FulfillmentFactory
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPayoutBounty:
    def test_payout_fails_when_not_logged_in(self):
        # fulfillment = FulfillmentFactory()
        # client = APIClient()
        # request_payload = {}

        # response = client.post(f'api/v1/bounty/payout/{fulfillment.id}', request_payload, format='json')

        # assert response.status_code == 400
        # assert 'error: user needs to be authenticated to fulfill bounty' in response.json.get('message')
        pass

    def test_payout_fails_when_user_does_not_have_profile(self):
        pass

    def test_payout_fails_when_the_request_is_not_a_post_request(self):
        pass

    def test_payout_fails_when_the_fulfillment_id_is_not_present(self):
        pass

    def test_payout_fails_when_bounty_fulfillment_does_not_exist(self):
        pass

    def test_payout_fails_when_bounty_state_is_cancelled_or_done(self):
        pass

    def test_payout_fails_when_user_is_not_the_funder(self):
        pass

    def test_payout_fails_when_payout_type_is_not_present(self):
        pass

    def test_payout_fails_when_payout_type_is_not_an_expected_type(self):
        pass

    def test_payout_type_fails_when_payout_type_is_manual_and_bounty_is_not_part_of_hackathon(self):
        pass

    def test_payout_type_fails_when_tenant_is_not_present(self):
        pass

    def test_payout_type_fails_when_amount_is_not_present(self):
        pass

    def test_payout_type_fails_when_token_name_is_not_present(self):
        pass

    # def test_payout_fails_when_funder_address_is_not_present(self, django_user_model):
        # """Test payout fails when funder_address is not present if payout_type is not 'fiat'."""
        # github_url = {'github_url': 'https://github.com/gitcoinco/web/issues/1'}
        # BountyFactory(**github_url)
        # user = django_user_model.objects.create(username="gitcoin", password="password123")
        # ProfileFactory(user=user)
        # fulfillment = FulfillmentFactory()

        # client = APIClient()

        # client.force_login(user)

        # payload = {
        #     'payout_type': 'manual',
        #     'tenant': 'test_tenant',
        #     'amount': '1',
        #     'token_name': 'ETH',
        # }

        # response = client.post(f'/api/v1/bounty/payout/{fulfillment.id}', payload)

        # assert response.status_code == 400
        # assert 'error: user needs to be authenticated to fulfill bounty' in response.json.get('message')


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

        #  const payload = {
        #     payout_type: payout_type,
        #     tenant: tenant,
        #     amount: amount,
        #     token_name: token_name,
        #     funder_address: funder_address,
        #     payout_tx_id: payout_tx_id
        #  };

