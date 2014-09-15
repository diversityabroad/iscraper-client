

1a) For Google search functionality, install the Google API Client
    pip install google-api-python-client

1b) For use with Python <2.7, install the following
    easy_install importlib 

2)  Set the following variables in settings.py

  2a)The search engine needs to be set

	SMARTSEARCH_AVAILABLE_ENGINES = {
	   'google': {
		     'CLASS':'djsmartsearch.engine.google.SearchEngine',
		     'GOOGLE_SITE_SEARCH_API_KEY':'',
		     'GOOGLE_SITE_SEARCH_SEID':'',
		     },
	}

  2b) (optional) This is the name of the logger to use.  The example below
  represents the default setting. If you want to capture logging, you also
  need to setup up loggers.  See the example project for a very basic example 
  of this. 

    SMARTSEARCH_LOGGER="smartsearch"

  2c) This is the url to search for the local site search. 

	# If using the Django site_config model backend
	
    SMARTSEARCH_LOCAL_SITE="www.osfsaintfrancis.org"

    # OR if using the Django site_config model_backend

	Set this variable in the admin intervace

  2d) Ensure the request context processor is set. 

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'django.core.context_processors.request',
    )

  2e) Add to installed apps: 

	# if using the django site_config settings backend

    INSTALLED_APPS = (
        ...
        'djsmartsearch',
    )
    
    # OR if using the Django site_config model_backend: 
    
    INSTALLED_APPS = (
        ...
        'djsmartsearch',
        'site_config',
        'site_config.backends.model_backend',
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
  
  2g) Add the site_config base_template context processor
  
    TEMPLATE_CONTEXT_PROCESSORS = (
      ...
      'site_config.context_processors.decide_base_template'
       ...
    )
  
  
3) Add the following to urls.py

    from djsmartsearch.views import DualSearchView

	# if using the django site_config settings backend

    urlpatterns = patterns('',
        url(r'^search/$', DualSearchView.as_view()),
        ....
    )

    # OR if using the Django site_config model_backend (and multi-site is desired):
    
    urlpatterns = patterns('',
        url(r'^(?P<website>[\w-]+)/search/$', DualSearchView.as_view()), 
        ....
    )
     
           

NOTES:

# To connect to the engine and do a search from the command line
from djsmartsearch.engine import  *
e = load_engines()
se = e['google']
se.search(query='joe')

   
