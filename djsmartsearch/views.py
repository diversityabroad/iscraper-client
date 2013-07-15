# Create your views here.
from djsmartsearch.cbv_fallback import FormView
from djsmartsearch import forms as smart_forms
from djsmartsearch.engine import  load_engines


class SearchView(FormView):

    query =''

    def __init__(self, *args, **kwargs):
        e = load_engines()
        self.engine = e[self.engine_name]
        super(SearchView, self).__init__(*args, **kwargs)


class DualGoogleSearchView(SearchView):
    
    template_name="djsmartsearch/search_dual.html"
    form_class = smart_forms.SearchForm
    engine_name = 'google'

    def form_valid(self, form):
        self.query = form.cleaned_data['query']
        if self.query:
            print self.query
            print self.engine
        print "HERE HERE HERE"
        return super(DualGoogleSearchView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({'query':self.query})
        return super(DualGoogleSearchView, self).get_context_data(**kwargs)