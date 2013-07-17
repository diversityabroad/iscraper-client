from djsmartsearch.engine import  *
e = load_engines()
se = e['google']
se.search(query='joe')


1a) For Google search functionality, install the Google API Client
    pip install google-api-python-client

1b) For use with Python <2.7, install the following
    easy_install importlib 

1c) For use with Python <2.6, install the following
	easy_install simplejson

2)  Set the following variables in settings.py

The search engine needs to be set

    SMARTSEARCH_AVAILABLE_ENGINES = [
        {'NAME':'google',
         'CLASS':'djsmartsearch.engine.google.SearchEngine',
         'GOOGLE_SITE_SEARCH_API_KEY':'',
         'GOOGLE_SITE_SEARCH_SEID':'',
         },
    ]


This is the name of the logger to use.  The example below
represents the default setting. 

    SMARTSEARCH_LOGGER="smartsearch"

This is the url to search for the local site search. 

    SMARTSEARCH_LOCAL_SITE="www.osfsaintfrancis.org"


Ensure the request context processor is set. 

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'django.core.context_processors.request',
    )

Add to installed apps: 

    INSTALLED_APPS = (
        ...
        'djsmartsearch',
    )

Set the cache backend to something: 
   
    # for Django <=1.2
    CACHE_BACKEND = 'locmem://'

    # for Django 1.3+
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        }
    }
    
4) Add the following to urls.py

    urlpatterns = patterns('',
        url(r'^search/$', DualGoogleSearchView.as_view()),
        ....
    )


    