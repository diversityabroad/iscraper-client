import logging
import math
try:
    import json
except ImportError:
    import simplejson as json 
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

    max_results_per_page = 10
    max_pages = 10

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
        page = kwargs.get('page', 1)
        if not page:
            page = 1
        elif page > self.max_pages:
            page = self.max_pages
        start = ((page - 1) * self.max_results_per_page) + 1
        num = kwargs.get('num', self.max_results_per_page)
        if not num:
            num = self.max_results_per_page
        try:
            response = self.connection.cse().list( q=kwargs.get('query', ''), cx=api_seid, 
                            num=self._get_num_results(num),
                            start=start).execute()
            logger.debug("Fetched search results for search term '%s'." % (kwargs.get('query', '')))
        except apiclient.errors.HttpError, e:
            logger.exception(e)
            raise 
        return response 

    def set_meta_from_response(self, response):
        meta = super(SearchEngine, self).set_meta_from_response(response)
        if response: 
            try:
                meta.update({'total_results':response['queries']['request'][0]['totalResults']})
            except:
                logger.debug("Unable to parse queries.request.total_results from response.")
                pass
            
            try:
                meta.update({'next_page_start':response['queries']['nextPage'][0]['startIndex']})
            except:
                logger.debug("Unable to parse queries.nextPage.startIndex from response.")
                pass
            
            try:
                meta.update({'previous_page_start':response['queries']['previousPage'][0]['startIndex']})
            except:
                logger.debug("Unable to parse queries.previousPage.startIndex from response.")
                pass
            
            try:
                start_index = response['queries']['request'][0]['startIndex']
                count = response['queries']['request'][0]['count']
                meta.update({'start_index':start_index})
                meta.update({'end_index':start_index - 1 + count})
                
                page = int(math.ceil(start_index / float(self.max_results_per_page)))
                meta.update({'page':page})
                if page > 1:
                   meta.update({'previous_page':page - 1})
                if page < self.max_pages:
                    meta.update({'next_page':page + 1}) 
                
                meta.update({'count':count})
            except Exception, e:
                logger.exception(e)
                pass

        return meta
        
    def get_iteration_root(self, response):
        return_value = []
        if isinstance(response, dict) and response.has_key('items'):
            return_value = response['items']
        return return_value
    
    def parse_row(self, row):
        return row
    