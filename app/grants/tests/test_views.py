from django.urls import reverse

from test_plus.test import TestCase


class GrantsViewResponsesTests(TestCase):
    def test_not_authorized(self):
        response = self.client.post(reverse('grants:new_matching_partner'))

        expected_response = {'message': 'Not Authorized', 'status': 403}
        self.assertEqual(response.status_code, expected_response['status'])
        self.assertEqual(response.json(), expected_response)
