import logging
import json
import apiclient
from django.conf import settings
from apiclient.discovery import build
from djsmartsearch.engine import SearchEngineBase
from djsmartsearch.engine import SMARTSEARCH_AVAILABLE_ENGINES

"""
The following needs to be set in settings.py for 
this search engine to operate properly. 

SMARTSEARCH_AVAILABLE_ENGINES = [
    {'NAME':'google',
     'CLASS':'djsmartsearch.engine.google.SearchEngine',
     'GOOGLE_SITE_SEARCH_API_KEY':'',
     'GOOGLE_SITE_SEARCH_SEID':'',
     },
]
"""
logger = logging.getLogger('%s.google' % getattr(settings, 'SMARTSEARCH_LOGGER', 'smartsearch'))


class SearchEngine(SearchEngineBase):

    max_results = 10

    def __init__(self, name='google'):
        self.engine_info = filter(lambda x: 'NAME' in x.keys() and x['NAME'] is name, SMARTSEARCH_AVAILABLE_ENGINES)[0]
        self.connection =  build('customsearch', 'v1', developerKey=self.engine_info['GOOGLE_SITE_SEARCH_API_KEY'])
        
    def fetch(self, query, num=None, start=1):
        api_seid = self.engine_info['GOOGLE_SITE_SEARCH_SEID']
        try:
            results = self.connection.cse().list( q=query, cx=api_seid, num=self._get_num_results(num), start=start).execute()
        except apiclient.errors.HttpError as e:
            logger.exception(e)
            raise 
        return results 
    
    def get_iteration_root(self, results):
        return_value = []
        if isinstance(results, dict):
            return_value = results['items']
        return return_value
    
    def parse_row(self, row):
        return row
    