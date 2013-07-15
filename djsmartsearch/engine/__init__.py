from django.conf import settings
import importlib

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


class SearchEngineBase(object):
    
    max_results = 10 # default max results
    
    def get_iteration_root(self):
        raise NotImplementedError("implement this get_iteration_root method in a subclass")
    
    def parse_row(self, row):
        raise NotImplementedError("implement this parse_row method in a subclass")

    def fetch(self,  *args, **kwargs):
        raise NotImplementedError("implement this fetch method in a subclass")
    
    def search(self, *args, **kwargs):
        results = self.fetch(*args, **kwargs)
        root = self._iterate(results)
        
    def _iterate(self, results):
        for item in self.get_iteration_root(results):
            yield self.parse_row(item)
            
    def _get_num_results(self, num):
        if not num:
            num = self.max_results
        if num > self.max_results:
            num = self.max_results
        return num