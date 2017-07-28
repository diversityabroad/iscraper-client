import math
import logging
import requests

from django.conf import settings
from djsmartsearch.engine import SearchEngineBase
from djsmartsearch.engine import SMARTSEARCH_AVAILABLE_ENGINES


"""
SMARTSEARCH_AVAILABLE_ENGINES = [
    {'NAME': 'iscape_search',
     'CLASS': 'djsmartsearch.engine.iscape_search.IscapeSearchEngine',
     'QUERY_ENDPOINT': '',
     'SEARCH_INDEX': ''  # the uuid of the config
     'ISCAPE_SEARCH_USER_KEY': 'user's user_key specified from iscape_search'
     },
]
"""
logger = logging.getLogger('%s.google' % getattr(settings, 'SMARTSEARCH_LOGGER', 'smartsearch'))


class IscapeSearchEngine(SearchEngineBase):

    max_results_per_page = 10
    max_pages = 10

    def __init__(self, name='iscape_search'):
        self.engine_info = filter(lambda x: 'NAME' in x.keys() and x['NAME'] is name, SMARTSEARCH_AVAILABLE_ENGINES)[0]

    def fetch(self, **kwargs):
        """
        Supported kwargs for this method
            - query = the search term to look for
            - num = the number of results to search for less than or equal to 10
            - start = an integer representing the search result to start on

          One can use this method to test the connection.
        """
        page = kwargs.get('page', 1)
        if page is None:
            page = 1
        elif page > self.max_pages:
            page = self.max_pages

        start_index = ((page - 1) * self.max_results_per_page)

        end_index = kwargs.get('num', start_index + self.max_results_per_page)
        if end_index is None:
            end_index = start_index + self.max_results_per_page

        data = {
            'query': kwargs.pop('query', ''),
            'index': self.engine_info['SEARCH_INDEX'],
            'page_start': start_index,
            'page_end': end_index,
            'user_key': self.engine_info['ISCAPE_SEARCH_USER_KEY']
        }

        try:
            response = requests.post(self.engine_info['QUERY_ENDPOINT'], data=data)
            response.raise_for_status()
        except Exception as e:  # this might have to change for bad responses...
            logger.exception(e)
            raise
        return response.json()

    def set_meta_from_response(self, response):
        meta = super(IscapeSearchEngine, self).set_meta_from_response(response)
        has_next_page = has_previous_page = True
        if response:
            try:
                total_results = response['meta']['total_results']
                meta['total_results'] = total_results
            except:
                logger.debug("Unable to parse queries.request.total_results from response.")
                pass

            try:
                start_index = response['meta']['start_index'] + 1
                end_index = response['meta']['end_index']

                has_previous_page = start_index - self.max_results_per_page > 0
                has_next_page = end_index < total_results

                page = int(math.ceil(start_index / float(self.max_results_per_page)))

                meta['start_index'] = start_index
                meta['end_index'] = end_index
                meta['page'] = page

                if page > 1 and has_previous_page:
                    meta['previous_page'] = page - 1
                if page < self.max_pages and has_next_page:
                    meta['next_page'] = page + 1

                meta['count'] = response['meta']['count']
            except Exception, e:
                logger.exception(e)
            return meta

    def get_iteration_root(self, response):
        return_value = []
        if isinstance(response, dict) and 'results' in response:
            return_value = response['results']
        return return_value

    def parse_row(self, row):
        return row