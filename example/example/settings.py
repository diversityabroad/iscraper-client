#################################
# This example project requires django 1.6
# This smartsearch2 'should' work with django 1.5+, but
# that is untested.  
#################################
from __future__ import unicode_literals

import sys, os
DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = PROJECT_DIR = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

sys.path.append(os.path.dirname(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, os.pardir)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$4#oc&+y!el(i#&j^$+cbx2(*z&$sxqkqe1x)frenrejcn!2c&'


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djsmartsearch',
    'site_config',
    'site_config.backends.model_backend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
   'django.contrib.auth.context_processors.auth', 
   'django.core.context_processors.debug', 
   'django.core.context_processors.i18n', 
   'django.core.context_processors.media', 
   'django.core.context_processors.static', 
   'django.core.context_processors.tz',
   'django.core.context_processors.request', 
   'django.contrib.messages.context_processors.messages',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'example.urls'

WSGI_APPLICATION = 'example.wsgi.application'



TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


CACHE_BACKEND = 'locmem://'

SITECONFIG_BACKEND_DEFAULT="site_config.backends.model_backend.DatabaseBackend"


SMARTSEARCH_AVAILABLE_ENGINES = {
   'google': {
         'CLASS':'djsmartsearch.engine.google.SearchEngine',
         'GOOGLE_SITE_SEARCH_API_KEY':'',
         'GOOGLE_SITE_SEARCH_SEID':'',
         },
}


SMARTSEARCH_LOCAL_SITE="www.osfsaintfrancis.org"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

######### LOGGING SECTION  #########
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'smartsearch': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


try:
    from local_settings import *
except ImportError:
    pass
