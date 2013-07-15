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
        raise NotImplementedError("implement this get_iteration_root method in a subclass")
    
    def parse_row(self, row):
        raise NotImplementedError("implement this parse_row method in a subclass")

    def _fetch_wrap(self, *args, **kwargs):
        try:
            results =  self.fetch(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            results = []
        return results 

    def fetch(self,  *args, **kwargs):
        raise NotImplementedError("implement this fetch method in a subclass")
    
    def search(self, *args, **kwargs):
        results = self._fetch_wrap(*args, **kwargs)
        result = self._iterate(results)
        yield result
        
    def _iterate(self, results):
        for item in self.get_iteration_root(results):
            yield self.parse_row(item)
            
    def _get_num_results(self, num):
        if not num:
            num = self.max_results
        if num > self.max_results:
            num = self.max_results
        return num