"""
Django settings for psmprj project.

See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import json
from . import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', 'secret key is in .env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)
ENV = env('ENV', "DEV")    # or PROD

# Disable admin
ADMIN = env.bool('DJANGO_ADMIN', True)

ALLOWED_HOSTS = [ '*' ]

# Application definition
INSTALLED_APPS = [

    'apis',
    'users.apps.UsersConfig',   # user extension (profile)
    'blog.apps.BlogConfig',     # blog
    'common',                   # common codes, utils, ...
    'psm',                      # main module
    'mtasks',                   # original task management (not used)
    'reports',                  # reporting
    'reviews',                  # reviews
    'data',                     # analytics (pilot)
    'resources',                # resource management (name resource is reserved by notebook)

    # 'guardian',               # object level permission management; django default is class level 

    # 'river',                  # simple workflow; not yet compatible with django 4.x

    'sorl.thumbnail',           # for blog thumnail
    'crispy_forms',             # for user form and blog forms
    'django_tables2',           # not used yet

    # 'django_filters'  ,       #bug with pagination

    # "django_crontab",
    "django_apscheduler",       # job scheduler

    'django_object_actions',    # for object-action

    # 'multi_email_field',  #not compatible with django 4.x
    
    'import_export',

    'adminfilters',         # https://github.com/mrsarm/django-adminfilters
    'django_admin_listfilter_dropdown', # https://github.com/mrts/django-admin-list-filter-dropdown
#    'jazzmin',                 # admin new UI
    
    'dal',                  # https://django-autocomplete-light.readthedocs.io/en/master/install.html#install-in-your-project
    'dal_select2',
    # "django.contrib.postgres",  # new for fulltext search (need POC)

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',    #debugging tool, jupyter
    
    'dbbackup',  # django-dbbackup

    # 'ckeditor',           # working fine, but not used here...
    # 'django_markdown',    # use different way markdown2
    # 'django.contrib.sites',   # what is this for???

#    'microsoft_auth',      # not working... need POC
#    'django_auth_adfs',    # not working... need POC, LDAP used instead
]

REST_ENABLED = env.bool('REST_ENABLED', False)
if REST_ENABLED:
    INSTALLED_APPS += ['rest_framework']

if not REST_ENABLED and not ADMIN:
    raise ValueError('You either have to enable REST_ENABLED or DJANGO_ADMIN')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'psmprj.urls'

#
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # project level templates
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # "django.template.context_processors.request",
#                'microsoft_auth.context_processors.microsoft',
            ],
        },
    },
]

#https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04
WSGI_APPLICATION = 'psmprj.wsgi.application'

#NGNIX -> Django : ensure to remove nignix default site 
# if "CSRF_TRUSTED_ORIGINS" in os.environ:
#     CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")     #["https://server-name-ip/", "http://server-name-ip/"]
# else:
#     CSRF_TRUSTED_ORIGINS = ["http://localhost"]
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", ["http://localhost",])     

#https://stackoverflow.com/questions/44034879/django-nginx-getting-csrf-verification-error-in-production-over-http
CSRF_COOKIE_HTTPONLY = env.bool('CSRF_COOKIE_HTTPONLY', False)
# https://stackoverflow.com/questions/28902243/multiple-django-sites-on-the-same-domain-csrf-fails
CSRF_COOKIE_NAME = env('CSRF_COOKIE_NAME', 'csrftoken')
SESSION_COOKIE_NAME = env('SESSION_COOKIE_NAME', 'sessionid')
SESSION_COOKIE_PATH = env('SESSION_COOKIE_PATH', '/')

#https://stackoverflow.com/questions/53788577/how-to-serve-subdirectory-as-root-in-nginx-using-django
#https://stackoverflow.com/questions/47941075/host-django-on-subfolder/47945170#47945170
# https://stackoverflow.com/questions/44987110/django-in-subdirectory-admin-site-is-not-working
# USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', False)
# USE_X_FORWARDED_HOST = True
# FORCE_SCRIPT_NAME = "/dj/"
# SESSION_COOKIE_PATH = '/dj/'

# Database settings
# from .settings_db import *
DB = env('DB', "SQLITE3")
if DB == "POSTGRES":
    #postgresql,  python -m pip install psycopg2
    DATABASES  = { 'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("POSTGRES_DB", "psmdb"), 
        'USER': env("POSTGRES_USER", 'postgres'), 
        'PASSWORD': env("POSTGRES_PASSWORD", "postgres"),
        'HOST': '127.0.0.1', 
        'PORT': '5432',
        },
    }
else:   #Development
    DATABASES = { 'default': env.dj_db_url('DATABASE_URL',
                            'sqlite:///%s/db.sqlite3' % BASE_DIR,
                            conn_max_age=env.int('CONN_MAX_AGE', 600)),

    }

# https://django-dbbackup.readthedocs.io/en/master/databases.html
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location':  env("DBBACKUP_LOCATION", BASE_DIR + "/backup")}
# DBBACKUP_CONNECTORS = {
#     'default': {
#         'USER': env("POSTGRES_USER", 'postgres'), 
#         'PASSWORD': env("POSTGRES_PASSWORD", "postgres"),
#         'HOST': '127.0.0.1', 
#     }
# }


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS_ENABLED = env.bool('AUTH_PASSWORD_VALIDATORS_ENABLED', True)
if AUTH_PASSWORD_VALIDATORS_ENABLED:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

# Misc settings: timezone, format, ...
from .settings_extra import *

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# https://docs.djangoproject.com/en/4.0/ref/settings/#staticfiles-dirs
# https://learndjango.com/tutorials/django-static-files
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', BASE_DIR + '/static/')
STATICFILES_DIRS = [BASE_DIR + '/psmprj/static',]    

# Whether to enable or not the StaticFilesHandler
# to serve the static resources from the WSGI
# server. Enabled by default if DEBUG = True,
# in production environmets it's recommended
# to serve the static resources with a reverse
# proxy like Nginx, unless little workloads
STATIC_ENABLE_WSGI_HANDLER = env.bool('STATIC_ENABLE_WSGI_HANDLER', False)

# Import settings for logging --------------------------------------------------
from .settings_logging import *

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissions',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
}

# Fileupload
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#https://github.com/edoburu/django-private-storage -> not working
# PRIVATE_STORAGE_ROOT = BASE_DIR + '/media-private/'
# PRIVATE_STORAGE_AUTH_FUNCTION = 'private_storage.permissions.allow_staff'

# export/import
#IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'import '

USE_LDAP = env.bool('USE_LDAP', False)
if USE_LDAP:
    # AzureAD SSO
    AUTHENTICATION_BACKENDS = [
    #    'django_auth_adfs.backend.AdfsAuthCodeBackend',
    #    'microsoft_auth.backends.MicrosoftAuthenticationBackend',
        # 'django_auth_ldap.backend.LDAPBackend',   #works fine, but group is not..
        'users.ldap.GroupLDAPBackend',
        'django.contrib.auth.backends.ModelBackend', # if you also want to use Django's authentication

        # I recommend keeping this with at least one database superuser in case of unable to use others
        # 'guardian.backends.ObjectPermissionBackend',
    ]

    # IMPORT Auth related settings ---------------------------------------
    from .settings_auth import *

#
# Custom configurations
#

APP_NAME = env('APP_NAME', 'PSM')
APP_EMAIL = env('APP_EMAIL', 'no-reply@localhost')
SITE_HEADER = env('SITE_HEADER', 'PSM')
INDEX_TITLE = env('INDEX_TITLE', 'PSM')

ADMINS = (
    (APP_NAME, APP_EMAIL)
)

# IMPORT EMAIL related settings ------------------------------------
from .settings_emails import *

# Default login https://docs.djangoproject.com/en/4.0/ref/settings/#login-url
LOGIN_URL = "login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# IMPORT Editor related settings ------------------------------------
from .settings_editor import *

# Load SAP connection settings

SAP = env.bool('SAP', False)
if SAP:
    SAP_CONFIG = json.load( open(os.path.join(BASE_DIR, '.sapcfg.json')) )
    SAP_CONN_WBS = SAP_CONFIG['servers'][env('SAP_RFC_WBS', '_')]

#https://github.com/jcass77/django-apscheduler
# https://stackoverflow.com/questions/62525295/how-to-use-python-to-schedule-tasks-in-a-django-application
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds

if ENV == "PROD":
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False    
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# -----------------------------------------------------------------------
# Cron tasks https://pypi.org/project/django-crontab/
# CRONJOBS = [
    # ('*/1 * * * *', 'psmprj.cron.database_backup'),
    # ('*/0 0 * * *', 'psmprj.cron.my_backup', {'verbose': 0}),
    # ('*/5 * * * *', 'myapp.cron.other_scheduled_job', ['arg1', 'arg2'], {'verbose': 0}),
    # ('0   4 * * *', 'django.core.management.call_command', ['clearsessions']),
# ]
# apscheduer start in users/apps.py

