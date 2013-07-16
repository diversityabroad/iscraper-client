# Create your views here.
from djsmartsearch.cbv_fallback import FormView
from djsmartsearch import forms as smart_forms
from djsmartsearch.engine import  load_engines
from django.core.cache import cache
from django.conf import settings

class SearchView(FormView):

    query =''
    results = {}
    meta = {}

    def __init__(self, *args, **kwargs):
        self.results = {}
        self.meta = {}
        e = load_engines()
        self.engine = e[self.engine_name]
        super(SearchView, self).__init__(*args, **kwargs)

    def get_cached(self, key):
        meta = {}
        results = []
        lookup = cache.get(key)
        if lookup:
            results, meta = lookup
        return results, meta
    
    def get_results(self, key, kwargs):
        results, meta = self.get_cached(key)
        if not results:
            result_iter, meta = self.engine.search(**kwargs)
            results = [ r for r in result_iter ]
            cache.set(key, (results, meta))
        return results, meta


class DualGoogleSearchView(SearchView):
    
    template_name="djsmartsearch/search_dual.html"
    result_include="djsmartsearch/includes/result_template_google.html"
    form_class = smart_forms.SearchForm
    engine_name = 'google'

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        self.start = form.cleaned_data['start']
        kwargs = {'query':self.query, 'start':self.start}
        if self.query:
            
            results_key = "results:%(query)s:%(start)s" % kwargs
            link_site = getattr(settings, 'SMARTSEARCH_LOCAL_SITE', None)
            local_kwargs = dict(query="site:%s %s" % (link_site, kwargs['query']), **{i:kwargs[i] for i in kwargs if i!='query'})
            self.results['local'], self.meta['local'] = self.get_results(results_key, local_kwargs)

            results_global_key = "global_%s" % (results_key)
            self.results['global'], self.meta['global'] = self.get_results(results_global_key, kwargs)

        return super(DualGoogleSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query':self.query, 
                       'results':self.results,
                       'result_include':self.result_include,
                       'meta':self.meta,
                       })
        return super(DualGoogleSearchView, self).get_context_data(**kwargs)