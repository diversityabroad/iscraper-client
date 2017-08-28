# The Google Search backend

1a) For Google search functionality, install the Google API Client
    pip install google-api-python-client

1b) For use with Python <2.7, install the following
    easy_install importlib

1c) For use with Python <2.6, install the following
	easy_install simplejson

2)  Set the following variables in settings.py

  2a)The search engine needs to be set

    SMARTSEARCH_AVAILABLE_ENGINES = [
        {'NAME':'google',
         'CLASS':'iscraper_client.engine.google.SearchEngine',
         'GOOGLE_SITE_SEARCH_API_KEY':'',
         'GOOGLE_SITE_SEARCH_SEID':'',
         },
    ]


  2b) (optional) This is the name of the logger to use.  The example below
  represents the default setting. If you want to capture logging, you also
  need to setup up loggers.  See the example project for a very basic example
  of this.

    SMARTSEARCH_LOGGER="smartsearch"

  2c) This is the url to search for the local site search.

    SMARTSEARCH_LOCAL_SITE="www.osfsaintfrancis.org"


  2d) Ensure the request context processor is set.

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'django.core.context_processors.request',
    )

  2e) Add to installed apps:

    INSTALLED_APPS = (
        ...
        'iscraper_client',
    )

  2f) Set the cache backend to something:

    # for Django <=1.2
    CACHE_BACKEND = 'locmem://'

    # for Django 1.3+
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        }
    }

3) Add the following to urls.py

    from iscraper_client.views import DualGoogleSearchView

    urlpatterns = patterns('',
        url(r'^search/$', DualGoogleSearchView.as_view()),
        ....
    )


NOTES:

# To connect to the engine and do a search from the command line
from iscraper_client.engine import  *
e = load_engines()
se = e['google']
se.search(query='joe')


# The iscape_search backend


1)  Set the following variables in settings.py

  1a)The search engine needs to be set

    SMARTSEARCH_AVAILABLE_ENGINES = [
        {
            'NAME': 'iscape_search',
            'CLASS': 'iscraper_client.engine.iscape_search.IscapeSearchEngine',
            'QUERY_ENDPOINT': '',  # the query endpoitn from iscape search
            'INSTALLATION_ID': '',  # the installation_id you'll be searching
            'ISCAPE_SEARCH_USER_KEY': '',  # your user_key that is set up in iscape_search
         },
    ]

    2b) (optional) This is the name of the logger to use.  The example below
    represents the default setting. If you want to capture logging, you also
    need to setup up loggers.  See the example project for a very basic example
    of this.

      SMARTSEARCH_LOGGER="smartsearch"

    2e) Add to installed apps:

      INSTALLED_APPS = (
          ...
          'iscraper_client',
      )

    3) Add the following to urls.py

        from iscraper_client.views import IscapeSearchView

        urlpatterns = patterns('',
            url(r'^search/$', IscapeSearchView.as_view()),
            ....
        )
