import math
import logging
import requests

from django.conf import settings
from iscraper_client.engine import SearchEngineBase
from iscraper_client.engine import SMARTSEARCH_AVAILABLE_ENGINES


"""
SMARTSEARCH_AVAILABLE_ENGINES = [
    {'NAME': 'iscape_search',
     'CLASS': 'iscraper_client.engine.iscape_search.IscapeSearchEngine',
     'QUERY_ENDPOINT': '',
     'INSTALLATION_ID': ''  # the uuid of the config
     'ISCAPE_SEARCH_USER_KEY': 'user's user_key specified from iscape_search'
     },
]
"""
logger = logging.getLogger(
    '%s' % getattr(settings, 'SMARTSEARCH_LOGGER', __name__))


def pretty_print_POST(req):
    print('{0}\n{1}\n{2}\n\n{3}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{0}: {1}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


class IscapeSearchEngine(SearchEngineBase):

    max_results_per_page = 10
    max_pages = 10

    def _constructe_engine_from_settings(self, name):
        def is_engine_present(_dict, name):
            return 'NAME' in _dict and _dict['NAME'] is name
        engine_info = [info for info in SMARTSEARCH_AVAILABLE_ENGINES if is_engine_present(info, name)]
        if engine_info:
            return engine_info[0]
        else:
            raise Exception("No engine named {0}, please check `SMARTSEARCH_AVAILABLE_ENGINES`"
                            "inside your `settings.py`".format(name))

    def __init__(self, name='iscape_search', config=None):
        if config:
            self.engine_info = config
        else:
            self.engine_info = self._constructe_engine_from_settings(name)

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

        headers = {
            'Username': self.engine_info['ISCAPE_SEARCH_USERNAME'],
            'Userkey': self.engine_info['ISCAPE_SEARCH_USER_KEY']
        }

        data = {
            'query': kwargs.pop('query', ''),
            'installation_id': self.engine_info['INSTALLATION_ID'],
            'page_start': start_index,
            'page_end': end_index,
        }

        req = requests.Request(
            'POST',
            self.engine_info['QUERY_ENDPOINT'],
            headers=headers,
            data=data)
        prepared_request = req.prepare()
        pretty_print_POST(prepared_request)
        session = requests.Session()
        session.verify = False

        try:
            response = session.send(prepared_request)
            logger.warning(" RESPONSE: {0}".format(response.content))
            response.raise_for_status()
        except Exception as e:  # this might have to change for bad responses...
            logger.exception(str(e))
        else:
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
                if end_index > total_results:
                    end_index = total_results

                page = int(math.ceil(start_index / float(self.max_results_per_page)))

                meta['start_index'] = start_index
                meta['end_index'] = end_index
                meta['page'] = page

                if page > 1 and has_previous_page:
                    meta['previous_page'] = page - 1
                if page < self.max_pages and has_next_page:
                    meta['next_page'] = page + 1

                meta['count'] = response['meta']['count']
            except Exception as e:
                logger.exception(e)
        return meta

    def search(self, *args, **kwargs):
        result_iter = []
        logger.debug("Searching with the following parameters %s" % (kwargs))
        response = self._fetch_wrap(*args, **kwargs)
        meta = self.set_meta_from_response(response)
        result_iter = self._iterate(response)
        recommended_iter = self._iterate(response, iteration_root='recommended_results')
        return result_iter, meta, recommended_iter

    def get_iteration_root(self, response, root='results'):
        return_value = []
        if isinstance(response, dict) and root in response:
            return_value = response[root]
        return return_value

    def parse_row(self, row):
        return row
