# Create your views here.
from iscraper_client.cbv_fallback import FormView
from iscraper_client import forms as smart_forms
from iscraper_client.engine import load_engines
from iscraper_client.decorators import check_recaptcha
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.conf import settings
from django.shortcuts import redirect


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
        self.recommended_results = {}
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
            results, meta, recommended_results = lookup
        return results, meta, recommended_results

    def get_context_data(self, **kwargs):
        google_site_key = getattr(settings, 'GOOGLE_SITE_KEY', None)
        if google_site_key:
            kwargs['google_site_key'] = google_site_key

        return super(SearchView, self).get_context_data(**kwargs)

    def get_results(self, key, kwargs, engine=None):
        """
        Perform the search and return the results.
        If a cached version of the results exist, return that.
        """
        results = meta = None
        if getattr(settings, 'SMARTSEARCH_USE_CACHE', True):
            results, meta = self.get_cached(key)
        if not results:
            if engine is None:
                result_iter, meta, recommended_iter = self.engine.search(**kwargs)
            else:
                result_iter, meta, recommended_iter = engine.search(**kwargs)

            results = [r for r in result_iter]
            recommended_results = [rr for rr in recommended_iter]
            if getattr(settings, 'SMARTSEARCH_USE_CACHE', True):
                cache.set(key, (results, meta, recommended_results))
        return results, meta, recommended_results


class IscapeSearchView(SearchView):

    template_name = 'iscapesearch/search_iscape.html'
    result_include = "iscraper_client/includes/result_template_iscape.html"
    recomennded_result_include = "iscraper_client/includes/recommended_result_template_iscape.html"
    engine_name = 'iscape_search'
    recommended_results = {}
    form_class = smart_forms.SearchForm

    def form_valid(self, form):
        self.query = form.cleaned_data['q']
        self.page = form.cleaned_data['page']

        if self.query:
            self.page = form.cleaned_data['page']
            kwargs = {'query': "%s" % (self.query), 'page': self.page}
            results_key = "results" + ":".join(map(lambda x: "%s" % x, kwargs.values()))
            self.results, self.meta, self.recommended_results = self.get_results(results_key, kwargs)

        for result in self.recommended_results:
            rec_result_type = result.get('type', None)
            if rec_result_type is not None and rec_result_type == 'redirect':
                redirect_url = result['redirect_url']
                return redirect(redirect_url)
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(check_recaptcha)
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(data=request.GET)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query': self.query,
                       'results': self.results,
                       'recommended_results': self.recommended_results,
                       'result_include': self.result_include,
                       'recommended_result_include': self.recomennded_result_include,
                       'meta': self.meta,  # Kept for backwards compat. Use search_meta when possible
                       'search_meta': self.meta,
                       })

        return super(IscapeSearchView, self).get_context_data(**kwargs)


class MultiSearchView(SearchView):

    template_name = 'iscapesearch/search_dual.html'
    result_include = "iscraper_client/includes/result_template_iscape.html"
    engine_name = 'iscape_search'
    form_class = smart_forms.DualSearchForm

    def __init__(self, *args, **kwargs):
        """
        Load the appropriate search engine and set defaults.
        """
        super(MultiSearchView, self).__init__(*args, **kwargs)
        self.engine1 = load_engines(config=settings.SMARTSEARCH_AVAILABLE_ENGINES[0])[self.engine_name]
        self.engine2 = load_engines(config=settings.SMARTSEARCH_AVAILABLE_ENGINES[1])[self.engine_name]

    @method_decorator(check_recaptcha)
    def get(self, request, *args, **kwargs):
        return super(MultiSearchView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.query = form.cleaned_data['q']
        self.page_one = form.cleaned_data['page_one']
        self.page_two = form.cleaned_data['page_two']

        if self.query:
            installation_one_kwargs = {'query': "%s" % (self.query), 'page': self.page_one}
            installation_one_key = "installation_one_results" + ":".join(map(
                lambda x: "%s" % x, installation_one_kwargs.values()))
            self.results['installation_one'], self.meta['installation_one'], self.recommended_results['installation_one'] = self.get_results(
                key=installation_one_key, kwargs=installation_one_kwargs, engine=self.engine1)

            # installtion two results
            installation_two_kwargs = {'query': "%s" % (self.query), 'page': self.page_two}
            installation_two_key = "installation_two_results" + ":".join(map(
                lambda x: "%s" % x, installation_two_kwargs.values()))
            self.results['installation_two'], self.meta['installation_two'], self.recommended_results['installation_two'] = self.get_results(
                key=installation_two_key, kwargs=installation_two_kwargs, engine=self.engine2
            )

        return super(MultiSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query': self.query,
                       'results': self.results,
                       'result_include': self.result_include,
                       'meta': self.meta,  # Kept for backwards compat. Use search_meta when possible
                       'search_meta': self.meta,
                       })
        return super(MultiSearchView, self).get_context_data(**kwargs)


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
            self.results['local'], self.meta['local'], self.recommended_results['local'] = self.get_results(results_key, local_kwargs)

            global_kwargs = {'query': self.query, 'page': self.page}
            results_global_key = "results_global" + ":".join(map(lambda x: "%s" % x, global_kwargs.values()))
            self.results['global'], self.meta['global'], self.recommended_results['global'] = self.get_results(results_global_key, global_kwargs)

        return super(DualGoogleSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query': self.query,
                       'results': self.results,
                       'result_include': self.result_include,
                       'meta': self.meta,
                       })
        return super(DualGoogleSearchView, self).get_context_data(**kwargs)
