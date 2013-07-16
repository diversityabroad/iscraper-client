# Create your views here.
from djsmartsearch.cbv_fallback import FormView
from djsmartsearch import forms as smart_forms
from djsmartsearch.engine import  load_engines
from django.core.cache import cache

class SearchView(FormView):

    query =''

    def __init__(self, *args, **kwargs):
        e = load_engines()
        self.engine = e[self.engine_name]
        super(SearchView, self).__init__(*args, **kwargs)


class DualGoogleSearchView(SearchView):
    
    template_name="djsmartsearch/search_dual.html"
    result_include="djsmartsearch/includes/result_template_google.html"
    form_class = smart_forms.SearchForm
    engine_name = 'google'
    results = []
    results_global = []
    meta = {}
    meta_global = {}

    def get_cached(self, key):
        meta = {}
        results = []
        lookup = cache.get(key)
        if lookup:
            results, meta = lookup
        return results, meta
            

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        self.start = form.cleaned_data['start']
        kwargs = {'query':self.query, 'start':self.start}
        if self.query:
            
            results_key = "results:%(query)s:%(start)s" % kwargs
            self.results, self.meta = self.get_cached(results_key)
            print "CACHED RESULTS", bool(self.results)
            if not self.results:
                result_iter, self.meta = self.engine.search(**kwargs)
                self.results = [ r for r in result_iter ]
                cache.set(results_key, (self.results, self.meta))
                
            results_global_key = "global_%s" % (results_key)
            self.results_global, self.meta_global = self.get_cached(results_global_key)
            print "CACHED GLOBAL RESULTS", bool(self.results_global)
            if not self.results_global:
                result_iter, self.meta_global = self.engine.search(**kwargs)
                self.results_global = [r for r in result_iter]
                cache.set(results_global_key, (self.results_global, self.meta_global))
             
        return super(DualGoogleSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query':self.query, 
                       'results':self.results,
                       'results_global':self.results_global, 
                       'result_include':self.result_include,
                       'meta':self.meta,
                       'meta_global':self.meta_global})
        return super(DualGoogleSearchView, self).get_context_data(**kwargs)