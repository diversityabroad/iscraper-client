from django.conf.urls import patterns, include, url

from djsmartsearch.views import DualSearchView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^search/$', DualSearchView.as_view()),
    (r'^admin/', include(admin.site.urls)),
)
