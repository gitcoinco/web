import json

from django.urls import reverse

from grants.views import basic_grant_categories
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
                ['devEx', 8],
                ['usability', 9],
                ['twitter', 10],
                ['reddit', 11],
                ['blog', 12],
                ['notes', 13],
                ['COVID19 research',14],
                ['COVID19 response',15]
            ],
            'status': 200
        }
        self.assertEqual(response.status_code, expected_response['status'])
        self.assertEqual(json.loads(response.content)['categories'], expected_response['categories'])

    def test_retrieving_all_categories(self):
        all_categories = basic_grant_categories('')

        expected_response = [
            ('security', 0),
            ('scalability',1),
            ('defi',2),
            ('education',3),
            ('wallets',4),
            ('community',5),
            ('eth2.0',6),
            ('eth1.x',7),
            ('devEx',8),
            ('usability',9),
            ('twitter', 10),
            ('reddit',11),
            ('blog',12),
            ('notes',13),
            ('COVID19 research',14),
            ('COVID19 response',15)
        ]

        self.assertEqual(all_categories, expected_response)

    def test_retrieving_tech_categories(self):
        tech_categories = basic_grant_categories('tech')

        expected_response = [
            ('security', 0),
            ('scalability',1),
            ('defi',2),
            ('education',3),
            ('wallets',4),
            ('community',5),
            ('eth2.0',6),
            ('eth1.x',7),
            ('devEx', 8),
            ('usability', 9)
        ]

        self.assertEqual(tech_categories, expected_response)

    def test_retrieving_media_categories(self):
        media_categories = basic_grant_categories('media')

        expected_response = [
            ('education',0),
            ('twitter', 1),
            ('reddit',2),
            ('blog',3),
            ('notes',4)
        ]

        self.assertEqual(media_categories, expected_response)
