from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from djsmartsearch.views import DualGoogleSearchView

urlpatterns = patterns('',

    url(r'^search/$', DualGoogleSearchView.as_view()),
    (r'^admin/', include(admin.site.urls)),
)
