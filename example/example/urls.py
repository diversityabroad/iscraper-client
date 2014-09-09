from django.conf.urls import patterns, include, url

from djsmartsearch.views import DualSearchView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # ADD THIS URL 
    url(r'^search/$', DualSearchView.as_view()),
    # or ADD THIS URL FOR MULTI_SITE
    url(r'^(?P<website>[\w-]+)/search/$', DualSearchView.as_view()),    
    (r'^admin/', include(admin.site.urls)),
)
