from __future__ import unicode_literals
import logging
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
import site_config
from django.views.generic import FormView
from djsmartsearch import forms as smart_forms
from djsmartsearch.engine import  load_engines
from django.core.cache import cache
from django.conf import settings
from .engine import SmartSearchConfig

logger = logging.getLogger('%s' % getattr(settings, 'SMARTSEARCH_LOGGER', 'djsmartsearch'))

class SearchView(FormView):

    query =''
    results = {}
    meta = {}

    def __init__(self, *args, **kwargs):
        """
        Load the appropriate search engine and set defaults. 
        """
        self.results = {}
        self.meta = {}
        self.engines = load_engines()
        super(SearchView, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.website = kwargs.get('website', None)
        self.config = SmartSearchConfig(website=self.website)
        self.engine = self.engines[self.get_engine()]
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_engine(self):
        return self.config.SMARTSEARCH_ENGINE

    def get_cached(self, key):
        """
        Lookup a given cache key and split out
        the search results and meta information from the key
        """
        key = quote(key)
        meta = {}
        results = []
        lookup = cache.get(key)
        if lookup:
            logger.debug("Search Cache Key Hit %s" % (key))
            results, meta = lookup
        return results, meta
    
    def get_results(self, key, kwargs):
        """
        Perform the search and return the results. 
        If a cached version of the results exist, return that.
        """
        results, meta = self.get_cached(key)
        if not results:
            logger.debug("Search Cache Key Miss %s" % (key))
            result_iter, meta = self.engine.search(**kwargs)
            results = [ r for r in result_iter ]
            cache.set(quote(key), (results, meta))
        return results, meta

    def get_context_data(self, **kwargs):
        kwargs.update({
                       'config':self.config,
                       'website':self.website,
                       })
        return super(SearchView, self).get_context_data(**kwargs)
    

class DualSearchView(SearchView):
    
    http_method_names = [u'get', u'post',]
    template_name="djsmartsearch/search_dual.html"
    result_include="djsmartsearch/includes/result_template_google.html"
    form_class = smart_forms.SearchForm

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_form_kwargs(self):
        
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('GET'):
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def form_valid(self, form):
        self.query = form.cleaned_data['q'].strip()
        self.page = form.cleaned_data['page']
        self.page_local = form.cleaned_data['page_local']
        
        if self.query:
            link_site = self.config.SMARTSEARCH_LOCAL_SITE
            local_kwargs = {'query':"site:%s %s" % (link_site, self.query), 'page':self.page_local}
            results_key = "results" + ":".join(map(lambda x: "%s" % x, local_kwargs.values()))
            self.results['local'], self.meta['local'] = self.get_results(results_key, local_kwargs)

            global_kwargs = {'query':self.query, 'page':self.page}
            results_global_key = "results_global" + ":".join(map(lambda x: "%s" % x, global_kwargs.values()))
            self.results['global'], self.meta['global'] = self.get_results(results_global_key, global_kwargs)

        return self.render_to_response(context=self.get_context_data(form=form), )

    def get_context_data(self, **kwargs):
        kwargs.update({'query':self.query, 
                       'results':self.results,
                       'result_include':self.result_include,
                       'meta':self.meta,
                       })
        return super(DualSearchView, self).get_context_data(**kwargs)
