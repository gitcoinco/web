import json

from django.urls import reverse

from test_plus.test import TestCase


class GrantsViewResponsesTests(TestCase):
    def test_not_authorized(self):
        response = self.client.post(reverse('grants:new_matching_partner'))

        expected_response = {'message': 'Not Authorized', 'status': 403}
        self.assertEqual(response.status_code, expected_response['status'])
        self.assertEqual(response.json(), expected_response)

    def test_fetching_grant_categories_from_api(self):
        response = self.client.get(reverse('grants:grant_categories'))

        expected_response = {
            'categories': [
                ['security', 0],
                ['scalability',1],
                ['defi',2],
                ['education',3],
                ['wallets',4],
                ['community',5],
                ['eth2.0',6],
                ['eth1.x',7],
            ],
            'status': 200
        }
        self.assertEqual(response.status_code, expected_response['status'])
        self.assertEqual(json.loads(response.content)['categories'], expected_response['categories'])
