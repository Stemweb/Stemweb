# Import locally configured settings 
from . import local_settings as ls
import os
import sys

DEBUG = True   ### if set to True, then Celery raises WARNING: "Using settings.DEBUG leads to a memory leak, never use this setting in production environments!

# Root folder of the site
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

ADMINS = (
    (ls.db_admin, ls.db_email),
)

MANAGERS = ADMINS

ALLOWED_HOSTS = ls.allowed_hosts
#ALLOWED_HOSTS = ['stemweb', 'localhost', '127.0.0.1']
#ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': ls.db_engine,    # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ls.db_name,        # Or path to database file if using sqlite3.
        'USER': ls.db_user,        # Not used with sqlite3.
        'PASSWORD': ls.db_pwd,     # Not used with sqlite3.
        'HOST': ls.db_host,        # Set to empty string for localhost. Not used with sqlite3.
        'PORT': ls.db_port,        # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-GB'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Lets force site.id to 1 so that fixtures/initial_data will change site's 
# name and domain to right ones with every syncdb command.
SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ls.secret_key


#MIDDLEWARE_CLASSES = (
#    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',    # can be disabled as workaround
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'Stemweb.third_party_apps.pagination.middleware.PaginationMiddleware',
#)

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',    # can be disabled as workaround
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'Stemweb.third_party_apps.pagination.middleware.PaginationMiddleware',
]

ROOT_URLCONF = ls.root_urls


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            os.path.join(SITE_ROOT, 'templates/'),
            os.path.join(SITE_ROOT, 'templates/stemweb'),
            os.path.join(SITE_ROOT, 'templates/algorithms'),
            os.path.join(SITE_ROOT, 'templates/registration'),
            os.path.join(SITE_ROOT, 'templates/files'),
        ],
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                #'django.template.context_processors.static',
                #'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                # insert your TEMPLATE_LOADERS here
                # List of callables that know how to import templates from various sources
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                #'django.template.loaders.eggs.Loader',
            ]
        },
    },
]


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'kombu',
    'redis',   
    #'rest_framework', 
    
    #'Stemweb.third_party_apps.recaptcha_works',
    #'Stemweb.third_party_apps.registration',
    'Stemweb.third_party_apps.pagination',
    
    # Own apps
    'Stemweb.home',
    'Stemweb.algorithms',
    'Stemweb.files',
)


# celery  configurations 
CELERY_BROKER_URL = ls.redis_server
CELERY_RESULT_BACKEND = ls.redis_server
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
INCLUDE=['Stemweb.algorithms.tasks']
#CELERY_TASK_ALWAYS_EAGER = True   ### always sync instead of async call; you can set it for debug purposes


# registration apps own setting. Configures how many days
# user has to activate account before it expires.
ACCOUNT_ACTIVATION_DAYS = 99
LOGIN_REDIRECT_URL = '/'

# number of days the results shall be kept as files and the meta infos shall be kept in DB
# used to prevent filling the file system and the database
KEEP_RESULTS_DAYS = 60

# Email backend
EMAIL_BACKEND = ls.email_backend

# E-mail settings. Needed for user registrations' confirmation.
# Later the site will probably send mails when algorithms runs
# complete, etc.
DEFAULT_FROM_EMAIL = ls.db_email
EMAIL_HOST = ls.email_host
EMAIL_HOST_USER = ls.email_host_user
EMAIL_HOST_PASSWORD = ls.email_host_pwd
EMAIL_PORT = ls.email_port
EMAIL_USE_TLS = ls.email_tls
#DEFAULT_FROM_EMAIL = "slinkola@cs.helsinki.fi"
#SERVER_EMAIL = "slinkola@cs.helsinki.fi"

# Recaptcha_works options
RECAPTCHA_PUBLIC_KEY  = ls.recaptcha_public_key
RECAPTCHA_PRIVATE_KEY = ls.recaptcha_private_key
RECAPTCHA_VALIDATION_OVERRIDE = True
RECAPTCHA_USE_SSL = True
RECAPTCHA_OPTIONS = {
    'theme': 'white',
    'lang': 'en',
    'tabindex': 0,
}

# Add small random delay to concurrency. 
# WATCHOUT: change when in production to False
CONCURRENT_RANDOM_DELAY = False

ROOT_LOG_DIR = os.path.join(SITE_ROOT, 'logs')
if not os.path.exists(ROOT_LOG_DIR):
	os.mkdir(ROOT_LOG_DIR);
	
ALGORITHMS_LOG_DIR = os.path.join(ROOT_LOG_DIR, 'algorithms')
if not os.path.exists(ALGORITHMS_LOG_DIR):
	os.makedirs(ALGORITHMS_LOG_DIR);
	
DJANGO_LOG_DIR = os.path.join(ROOT_LOG_DIR, '_django')
if not os.path.exists(DJANGO_LOG_DIR):
	os.makedirs(DJANGO_LOG_DIR);

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
		'algorithm_run': {
			'format': '%(levelname)s %(asctime)s %(module) pid:%(process)d %(message)s'
		}
    },
	'filters': { },
   
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'logging.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
		'algorithm_run': {
			'level':'DEBUG',
			'class':'logging.handlers.TimedRotatingFileHandler',
			'formatter': 'verbose',
			'filename': os.path.join(ALGORITHMS_LOG_DIR, 'runs'),
			'when': 'D',
			#'interval': 1,
		},
		'authentication': {
			'level':'DEBUG',
			'class':'logging.handlers.TimedRotatingFileHandler',
			'formatter': 'verbose',
			'filename': os.path.join(ALGORITHMS_LOG_DIR, 'auth'),
			'when': 'D',
			#'interval': 1,
		},
		
		'file': {
			'level':'DEBUG',
			'class':'logging.handlers.TimedRotatingFileHandler',
			'formatter': 'verbose',
			'filename': os.path.join(DJANGO_LOG_DIR, 'myLogFile.txt'),
			'when': 'D',
			#'filemode': 'a'
			#'interval': 1,
		},
    	#'celery_tasks': {
		#	'level':'DEBUG',
		#	'class':'logging.handlers.TimedRotatingFileHandler',
		#	'formatter': 'verbose',
		#	'filename': os.path.join(ALGORITHMS_LOG_DIR, 'tasks'),
		#	'when': 'D',
		#	#'interval': 1,    
        #}    
    },
    'loggers': {
		'stemweb.algorithm_run': {
			'handlers': ['console', 'algorithm_run'],
			'propagate': False,
			'level': 'DEBUG',
		},
        'django': {
            'handlers':['console', 'file'],
            'propagate': True,
            'level':'DEBUG',
        },
		'stemweb.auth': {
			'handlers': ['console', 'authentication'],
			'propagate': False,
			'level': 'DEBUG',
		},
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            #'handlers': ['console','celery_tasks'],
            'handlers': ['console'],            
            'level': 'DEBUG',
            'propagate': True
        }      

    }
}
