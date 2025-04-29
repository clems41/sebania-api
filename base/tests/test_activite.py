import json

from django.urls import reverse_lazy
from rest_framework import status

from sebania.tests.SebaniaTestCase import SebaniaTestCase


class TestActivite(SebaniaTestCase):
    url = reverse_lazy('configurations-get-activites')

    def _get_response_for_keyword(self, keyword, expected_status_code=status.HTTP_200_OK):
        query = {}
        if keyword:
            query['query'] = keyword
        response =  self.client.get(self.url, query_params=query)
        self.assertEqual(response.status_code, expected_status_code)
        if expected_status_code == status.HTTP_200_OK:
            return json.loads(response.content)
        return None

    def test_search_activites_without_query(self):
        response = self._get_response_for_keyword(None)
        self.assertEqual(len(response), 57)


    def test_search_activites(self):
        expected = {
            'plant': [1,7,8],
            'logist': [20,21,26],
            'semis': [1,7],
            'compost': [3,41],
            'semis direct': [1,7,24],
            'traitement maladie': [10],
            'destruction insecte': [10, 15, 55],
        }
        for query, expected_activite_ids in expected.items():
            response = self._get_response_for_keyword(query)
            self.assertEqual(len(response), len(expected_activite_ids))
            for expected_activite_id in expected_activite_ids:
                self.assertTrue(expected_activite_id in [activite.get('id') for activite in response])


    def test_search_activites_query_incorrect(self):
        self._get_response_for_keyword("dc", expected_status_code=status.HTTP_400_BAD_REQUEST)

