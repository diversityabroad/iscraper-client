from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import http

"""
Since this project may be deployed on Django version 1.0, I am 
creating a simple Generic Class-based view system based loosely 
on the 1.3+ syntax. 
"""

class FormView(object):

    http_method_names = ['get',]
    form_class = None

    @classmethod
    def as_view(cls,  **initkwargs):
        
        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)
        
        return view 

    def get_form_class(self):
        return self.form_class

    def get_context_data(self, **kwargs):
        return kwargs

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(data=request.GET)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)        

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
            extra={
                'status_code': 405,
                'request': self.request
            }
        )
        return http.HttpResponseNotAllowed(self._allowed_methods())

    def render_to_response(self, context):
        return render_to_response(self.template_name, context,
                      context_instance=RequestContext(self.request))
