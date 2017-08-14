"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import mock
import json
from django.test import TestCase

from djsmartsearch.engine.iscape_search import IscapeSearchEngine


class IscapeSearchTests(TestCase):

    mock_search_results = {
        "meta": {
            "end_index": 10,
            "count": 2,
            "start_index": 0,
            "total_results": 2
        },
        "results": [{
            "//www.golosa.org/kresling": {
                "always": {
                    "title": "Golosa",
                    "h1": "The Russian Folksong at the University of Freiburg"
                },
                "hits": [{
                    "content": "The singers are students, and therefore as nationally diverse as any typical student body, and their director left <strong>Russia</strong> nearly sixty years ago in 1919. "
                }]
            }
        }, {
            "//www.golosa.org/history": {
                "always": {
                    "title": "Golosa",
                    "h1": "A Brief History of Golosa"
                },
                "hits": [{
                    "content": "The songs as we have them today are descended from songs heard in the earliest of years of the twentieth century in villages throughout <strong>Russia</strong>; and those songs in turn were merely the latest incarnation of music many years older still. "
                }]
            }
        }]
    }

    def mocked_requests_session_send(self, *args, **kwargs):
        class MockResponse:
            def __init__(self, data, status_code):
                self.data = data
                self.status_code = status_code

            def json(self):
                return self.data

            def raise_for_status(self):
                pass

            @property
            def content(self):
                json_str = json.dumps(self.data)
                return '{0}'.format(json_str)

        return MockResponse(self.mock_search_results, 200)

    def mocked_session(self, *arg, **kwargs):
        class MockSession:
            def __init__(self, response):
                self.response = response

            def send(self, prepared_request):
                return self.response

        return MockSession(self.mocked_requests_session_send())

    def mocked_request(self, *arg, **kwargs):
        class MockRequest:
            def __init__(self, method, url, headers, body):
                self.method = method
                self.url = url
                self.headers = headers
                self.body = body

            def prepare(self):
                return self

        return MockRequest('POST',
                           'http://localhost.com/api/v1/search',
                           {'Username': 'admin', 'Userkey': 'SomeKey'},
                           "post data bytes")

    search_config = {
        'INSTALLATION_ID': 'just some uuid',
        'QUERY_ENDPOINT': 'just some url',
        'ISCAPE_SEARCH_USER_KEY': 'just some userkey',
        'ISCAPE_SEARCH_USERNAME': 'just some username'
    }

    def test_search(self):
        with mock.patch('requests.Session', side_effect=self.mocked_session):
            with mock.patch('requests.Request', side_effect=self.mocked_request):
                engine = IscapeSearchEngine(config=self.search_config)

                query = {'q': 'russia'}
                kwargs = {'query': "%s" % (query), 'page': 1}
                result_iter, meta = engine.search(**kwargs)
                results = [r for r in result_iter]

                self.assertEqual(meta['total_results'], 2)
                self.assertEqual(meta['start_index'], 1)
                self.assertEqual(meta['end_index'], 2)
                self.assertEqual(meta['count'], 2)
                self.assertEqual(meta['page_next'], None)
                self.assertEqual(meta['page_previous'], None)

                self.assertEqual(results, self.mock_search_results['results'])
