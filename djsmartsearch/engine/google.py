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
        """
        Find the google search engine backend and establish a connection object.
        """
        self.engine_info = filter(lambda x: 'NAME' in x.keys() and x['NAME'] is name, SMARTSEARCH_AVAILABLE_ENGINES)[0]
        self.connection =  build('customsearch', 'v1', developerKey=self.engine_info['GOOGLE_SITE_SEARCH_API_KEY'])
    
    def fetch(self,  **kwargs):
        """
        Supported kwargs for this method
          - query = the search term to look for
          - num = the number of results to search for less than or equal to 10
          - start = an integer representing the search result to start on
        
        One can use this method to test the connection. 
        """
        api_seid = self.engine_info['GOOGLE_SITE_SEARCH_SEID']
        try:
            response = self.connection.cse().list( q=kwargs.get('query', ''), cx=api_seid, 
                            num=self._get_num_results(kwargs.get('num', None)),
                            start=kwargs.get('start', 1)).execute()
        except apiclient.errors.HttpError as e:
            logger.exception(e)
            raise 
        return response 

    def set_meta_from_results(self, resutls):
        meta = {}
        try:
            meta.update({'total_results':resutls['queries']['request'][0]['totalResults']})
        except:
            pass
        
        try:
            meta.update({'next_page_start':resutls['queries']['nextPage'][0]['startIndex']})
        except:
            pass
        
        try:
            meta.update({'previous_page_start':resutls['queries']['previousPage'][0]['startIndex']})
        except:
            pass
                
        return meta
        
    def get_iteration_root(self, results):
        return_value = []
        if isinstance(results, dict) and results.has_key('items'):
            return_value = results['items']
        return return_value
    
    def parse_row(self, row):
        return row
    