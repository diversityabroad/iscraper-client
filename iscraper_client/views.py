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

    engine_name = None  # should be overridden in subclass

    def __init__(self, *args, **kwargs):
        """
        Load the appropriate search engine and set defaults.
        """
        if 'template_name' in kwargs:
            self.template_name = kwargs.pop('template_name')
        if 'result_include' in kwargs:
            self.result_include = kwargs.pop('result_include')
        self.query = ""
        self.results = []
        self.meta = {}
        self.recommended_results = []
        self.engine = load_engines()[self.engine_name]
        super(SearchView, self).__init__(*args, **kwargs)

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
        results = None
        if getattr(settings, 'SMARTSEARCH_USE_CACHE', True):
            results = cache.get(key, None)

        if not results:
            if engine:
                result_iter, meta, recommended_iter = engine.search(**kwargs)
            else:
                result_iter, meta, recommended_iter = self.engine.search(**kwargs)

            # Make a dictionary comprising everything we get back from the
            # search engine. Yes, it's confusing that "results" contains a
            # key called "results".
            results = {
                "results": [r for r in result_iter],
                "meta": meta,
                "recommended_results": [rr for rr in recommended_iter]
            }
            if getattr(settings, 'SMARTSEARCH_USE_CACHE', True):
                cache.set(key, results)
        return results


class IscapeSearchView(SearchView):

    template_name = 'iscapesearch/search_iscape.html'
    result_include = "iscraper_client/includes/result_template_iscape.html"
    recommended_result_include = "iscraper_client/includes/recommended_result_template_iscape.html"
    engine_name = 'iscape_search'
    form_class = smart_forms.SearchForm

    def form_valid(self, form):
        self.query = form.cleaned_data['q']
        self.page = form.cleaned_data['page']

        if self.query:
            self.page = form.cleaned_data['page']
            kwargs = {'query': "%s" % (self.query), 'page': self.page}
            results_key = "results" + ":".join(map(lambda x: "%s" % x, kwargs.values()))
            results_dict = self.get_results(results_key, kwargs)
            self.results = results_dict.get("results", [])
            self.meta = results_dict.get("meta", {})
            self.recommended_results = results_dict.get("recommended_results", [])

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
                       'recommended_result_include': self.recommended_result_include,
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
            # installation one results
            installation_one_kwargs = {'query': "%s" % (self.query), 'page': self.page_one}
            installation_one_key = "installation_one_results" + ":".join(map(
                lambda x: "%s" % x, installation_one_kwargs.values()))

            results_dict = self.get_results(
                key=installation_one_key,
                kwargs=installation_one_kwargs,
                engine=self.engine1
            )
            self.results['installation_one'] = results_dict.get("results", [])
            self.meta['installation_one'] = results_dict.get("meta", {})
            self.recommended_results['installation_one'] = results_dict.get("recommended_results", [])
            
            # installation two results
            installation_two_kwargs = {'query': "%s" % (self.query), 'page': self.page_two}
            installation_two_key = "installation_two_results" + ":".join(map(
                lambda x: "%s" % x, installation_two_kwargs.values()))

            results_dict = self.get_results(
                key=installation_two_key,
                kwargs=installation_two_kwargs,
                engine=self.engine2
            )
            self.results['installation_two'] = results_dict.get("results", [])
            self.meta['installation_two'] = results_dict.get("meta", {})
            self.recommended_results['installation_two'] = results_dict.get("recommended_results", [])

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

            results_dict = self.get_results(
                key=results_key,
                kwargs=local_kwargs
            )
            self.results['local'] = results_dict.get("results", [])
            self.meta['local'] = results_dict.get("meta", {})
            self.recommended_results['local'] = results_dict.get("recommended_results", [])

            global_kwargs = {'query': self.query, 'page': self.page}
            results_global_key = "results_global" + ":".join(map(lambda x: "%s" % x, global_kwargs.values()))

            results_dict = self.get_results(
                key=results_global_key,
                kwargs=global_kwargs
            )
            self.results['global'] = results_dict.get("results", [])
            self.meta['global'] = results_dict.get("meta", {})
            self.recommended_results['global'] = results_dict.get("recommended_results", [])

        return super(DualGoogleSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query': self.query,
                       'results': self.results,
                       'result_include': self.result_include,
                       'meta': self.meta,
                       })
        return super(DualGoogleSearchView, self).get_context_data(**kwargs)
