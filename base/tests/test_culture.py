import json

from django.urls import reverse_lazy
from rest_framework import status

from sebania.tests.SebaniaTestCase import SebaniaTestCase


class TestCulture(SebaniaTestCase):
    url = reverse_lazy('configurations-get-cultures')

    def _get_response_for_keyword(self, keyword, expected_status_code=status.HTTP_200_OK):
        query = {}
        if keyword:
            query['query'] = keyword
        response =  self.client.get(self.url, query_params=query)
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code == status.HTTP_200_OK:
            return json.loads(response.content)
        return None

    def test_search_cultures_without_query(self):
        response = self._get_response_for_keyword(None)
        self.assertEqual(len(response), 53)


    def test_search_cultures(self):
        expected = {
            'chou': [10,11,12,13,14,48,53],
            'courge': [16,17,18],
            'tom': [43],
            'butternut': [8],
            'Chou-fleur': [14],
            'Céler': [19,20],
        }
        for query, expected_culture_ids in expected.items():
            response = self._get_response_for_keyword(query)
            self.assertEqual(len(response), len(expected_culture_ids))
            for expected_culture_id in expected_culture_ids:
                self.assertTrue(expected_culture_id in [culture.get('id') for culture in response])


    def test_search_cultures_query_incorrect(self):
        self._get_response_for_keyword("dc", expected_status_code=status.HTTP_400_BAD_REQUEST)

