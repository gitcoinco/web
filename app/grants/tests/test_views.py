import json

from django.urls import reverse

from grants.models import Grant, GrantCategory, GrantType
from grants.views import basic_grant_categories
from test_plus.test import TestCase


class GrantsViewResponsesTests(TestCase):
    # def test_not_authorized(self):
        # response = self.client.post(reverse('grants:new_matching_partner'))


        # expected_response = {'status': 200}
        # self.assertEqual(response.status_code, expected_response['status'])

    def test_fetching_grant_categories_from_api(self):
        '''
        response = self.client.get(reverse('grants:grant_categories'))

        if GrantCategory.objects.all().count == 0:
            return

        result = []
        for category in GrantCategory.objects.all():
            result.append(category.category)

        result = list(set(result))
        categories = [ (category,idx) for idx, category in enumerate(result) ]

        expected_response = {
            'categories': categories,
            'status': 200
        }

        self.assertEqual(response.status_code, expected_response['status'])
        self.assertEqual(json.loads(response.content)['categories'], expected_response['categories'])
        '''
        pass
