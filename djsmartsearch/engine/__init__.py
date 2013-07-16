import logging
import importlib
from django.conf import settings

SMARTSEARCH_AVAILABLE_ENGINES=[]

if hasattr(settings, 'SMARTSEARCH_AVAILABLE_ENGINES'):
    SMARTSEARCH_AVAILABLE_ENGINES = settings.SMARTSEARCH_AVAILABLE_ENGINES

def load_engines():

    engines = {}
    for engine in SMARTSEARCH_AVAILABLE_ENGINES:
        klass_str = "".join(engine['CLASS'].split(".")[-1:])
        module_str = ".".join(engine['CLASS'].split(".")[:-1])
        module = importlib.import_module(module_str)
        backend = getattr(module, klass_str)
        engines[engine['NAME']] = backend(name=engine['NAME'])
    return engines

logger = logging.getLogger(getattr(settings, 'SMARTSEARCH_LOGGER', 'smartsearch'))

class SearchEngineBase(object):
    
    max_results = 10 # default max results
    
    def get_iteration_root(self):
        """
        Returns the iterable at the root of the search results. 
        """
        raise NotImplementedError("implement this get_iteration_root method in a subclass")
    
    def parse_row(self, row):
        """
        Provide any logic to specifically parse a given result row. 
        """
        raise NotImplementedError("implement this parse_row method in a subclass")

    def set_meta_from_results(self, resutls):
        """
        Should make a call to set_meta(), passing any meta keywords
        and return the results.  This returns no meta data by default 
        """
        return self.set_meta()
    
    def fetch(self,  *args, **kwargs):
        """
        Issues the command to actually make the network request to fetch the
        response. 
        """
        raise NotImplementedError("implement this fetch method in a subclass")

    def _fetch_wrap(self, *args, **kwargs):
        try:
            response =  self.fetch(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            response = []
        return response 

    def search(self, *args, **kwargs):
        response = self._fetch_wrap(*args, **kwargs)
        meta = self.set_meta_from_results(response)
        result_iter = self._iterate(response)
        return result_iter, meta
        
    def _iterate(self, response):
        if response:
            for item in self.get_iteration_root(response):
                yield self.parse_row(item)
            
    def _get_num_results(self, num):
        if not num:
            num = self.max_results
        if num > self.max_results:
            num = self.max_results
        return num