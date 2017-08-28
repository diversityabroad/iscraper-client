# Create your views here.
from iscraper_client.cbv_fallback import FormView
from iscraper_client import forms as smart_forms
from iscraper_client.engine import load_engines
from django.core.cache import cache
from django.conf import settings


class SearchView(FormView):

    query = ''
    results = {}
    meta = {}

    def __init__(self, *args, **kwargs):
        """
        Load the appropriate search engine and set defaults.
        """
        if 'template_name' in kwargs:
            self.template_name = kwargs.pop('template_name')
        if 'result_include' in kwargs:
            self.result_include = kwargs.pop('result_include')
        self.results = {}
        self.meta = {}
        self.engine = load_engines()[self.engine_name]
        super(SearchView, self).__init__(*args, **kwargs)

    def get_cached(self, key):
        """
        Lookup a given cache key and split out
        the search results and meta information from the key
        """
        meta = {}
        results = []
        lookup = cache.get(key)
        if lookup:
            results, meta = lookup
        return results, meta

    def get_results(self, key, kwargs):
        """
        Perform the search and return the results.
        If a cached version of the results exist, return that.
        """
        results = meta = None
        if getattr(settings, 'SMARTSEARCH_USE_CACHE', True):
            results, meta = self.get_cached(key)
        if not results:
            result_iter, meta = self.engine.search(**kwargs)

            results = [r for r in result_iter]
            if getattr(settings, 'SMARTSEARCH_USE_CACHE', True):
                cache.set(key, (results, meta))
        return results, meta


class IscapeSearchView(SearchView):

    template_name = 'iscapesearch/search_iscape.html'
    result_include = "iscraper_client/includes/result_template_iscape.html"
    engine_name = 'iscape_search'
    form_class = smart_forms.SearchForm

    def form_valid(self, form):
        self.query = form.cleaned_data['q']
        self.page = form.cleaned_data['page']

        if self.query:
            self.page = form.cleaned_data['page']
            kwargs = {'query': "%s" % (self.query), 'page': self.page}
            results_key = "results" + ":".join(map(lambda x: "%s" % x, kwargs.values()))
            self.results, self.meta = self.get_results(results_key, kwargs)

        return super(IscapeSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query': self.query,
                       'results': self.results,
                       'result_include': self.result_include,
                       'meta': self.meta, # Kept for backwards compat. Use search_meta when possible
                       'search_meta': self.meta,
                       })

        return super(IscapeSearchView, self).get_context_data(**kwargs)


class DualGoogleSearchView(SearchView):

    template_name = "iscraper_client/search_dual.html"
    result_include = "iscraper_client/includes/result_template_google.html"
    form_class = smart_forms.SearchForm
    engine_name = 'google'

    # I'll have to test passing in vars with this...
    def form_valid(self, form):
        self.query = form.cleaned_data['q']
        self.page = form.cleaned_data['page']
        self.page_local = form.cleaned_data['page_local']

        if self.query:

            link_site = getattr(settings, 'SMARTSEARCH_LOCAL_SITE', None)
            local_kwargs = {'query': "site:%s %s" % (link_site, self.query), 'page': self.page_local}
            results_key = "results" + ":".join(map(lambda x: "%s" % x, local_kwargs.values()))
            self.results['local'], self.meta['local'] = self.get_results(results_key, local_kwargs)

            global_kwargs = {'query': self.query, 'page': self.page}
            results_global_key = "results_global" + ":".join(map(lambda x: "%s" % x, global_kwargs.values()))
            self.results['global'], self.meta['global'] = self.get_results(results_global_key, global_kwargs)

        return super(DualGoogleSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query': self.query,
                       'results': self.results,
                       'result_include': self.result_include,
                       'meta': self.meta,
                       })
        return super(DualGoogleSearchView, self).get_context_data(**kwargs)
