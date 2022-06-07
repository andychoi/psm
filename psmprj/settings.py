"""
Django settings for psmprj project.

See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
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
#    'jazzmin',
    # 'mtasks.apps.MtasksConfig',
    # 'CBU',
    'common',
    'psm',
    'mtasks',
    'reports',
    'reviews',

    # 'resources',
    
    'guardian',      # object level permission management; django default is class level 
#    'river',        # simple workflow; not yet compatible with django 4.x
    # blog
    'users.apps.UsersConfig',
    'blog.apps.BlogConfig',
    'crispy_forms',
    'django_tables2',
    # 'django_filters'  ,   #bug with pagination

    # 'multi_email_field',  #not compatible with django 4.x
    'django_object_actions', 

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',    #debugging tool
    'import_export',
    'django_admin_listfilter_dropdown',
    'adminfilters',

    # 'ckeditor',
    # 'django_markdown',
#    'django.contrib.sites',
#    'microsoft_auth',
#    'django_auth_adfs',
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
#CSRF_COOKIE_HTTPONLY = env.bool('CSRF_COOKIE_HTTPONLY', False)

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

#
# Database config is passed in environment variable DATABASE_URL
# as string connection like postgresql://dpsmprj:postgres@localhost/dpsmprj_dev,
# otherwise the default SQLite database below is used.
# See more options at https://github.com/kennethreitz/dj-database-url
#
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


TIME_ZONE = env('TIME_ZONE', 'America/Los_Angeles')
USE_TZ = True

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = env('LANGUAGE_CODE', 'en-us')
USE_I18N = True
USE_L10N = True
# from django.conf.locale.es import formats as es_formats
# es_formats.DATETIME_FORMAT = 'd M Y, H:i'
# es_formats.DATE_FORMAT = 'd M, Y'
from django.conf.locale.en import formats as en_formats
#en_formats.DATETIME_FORMAT = 'M d Y, H:i'
en_formats.DATETIME_FORMAT = 'm/d/y g:i a'
# en_formats.DATE_FORMAT = 'M d, Y'
en_formats.DATE_FORMAT = 'Y-m-d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# https://docs.djangoproject.com/en/4.0/ref/settings/#staticfiles-dirs
# https://learndjango.com/tutorials/django-static-files
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', BASE_DIR + '/static/')
STATICFILES_DIRS = [BASE_DIR + '/psmprj/static',]    
# if ENV == "PROD":
#     # python manage.py collectstatic - how to include project level static files?
#     STATIC_ROOT = env('STATIC_ROOT', BASE_DIR + '/static/')
#     STATICFILES_DIRS = [os.path.join('psmprj', 'static'),]    

# else:
#     STATIC_ROOT = env('STATIC_ROOT', BASE_DIR + '/static/')
#     STATICFILES_DIRS = [os.path.join('psmprj', 'static'),]    


# Whether to enable or not the StaticFilesHandler
# to serve the static resources from the WSGI
# server. Enabled by default if DEBUG = True,
# in production environmets it's recommended
# to serve the static resources with a reverse
# proxy like Nginx, unless little workloads
STATIC_ENABLE_WSGI_HANDLER = env.bool('STATIC_ENABLE_WSGI_HANDLER', DEBUG)

from .settings_logging import *

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Fileupload
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#form templates
CRISPY_TEMPLATE_PACK = 'bootstrap4'

#https://github.com/edoburu/django-private-storage -> not working
# PRIVATE_STORAGE_ROOT = BASE_DIR + '/media-private/'
# PRIVATE_STORAGE_AUTH_FUNCTION = 'private_storage.permissions.allow_staff'

# export/import
#IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'import '

# AzureAD SSO
AUTHENTICATION_BACKENDS = [
#    'django_auth_adfs.backend.AdfsAuthCodeBackend',
#    'microsoft_auth.backends.MicrosoftAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend', # if you also want to use Django's authentication
    # I recommend keeping this with at least one database superuser in case of unable to use others
    'guardian.backends.ObjectPermissionBackend',
]

# from decouple import config
# # values you got from step 2 from your Mirosoft app
# MICROSOFT_AUTH_CLIENT_ID = config("MICROSOFT_AUTH_CLIENT_ID")
# MICROSOFT_AUTH_CLIENT_SECRET = config("MICROSOFT_AUTH_CLIENT_SECRET")
# # Tenant ID is also needed for single tenant applications
# MICROSOFT_AUTH_TENANT_ID = config("MICROSOFT_AUTH_TENANT_ID")
# MICROSOFT_AUTH_LOGIN_TYPE = 'ma'

# client_id = config("MICROSOFT_AUTH_CLIENT_ID")
# client_secret = config("MICROSOFT_AUTH_CLIENT_SECRET")
# tenant_id = config("MICROSOFT_AUTH_TENANT_ID")
# AUTH_ADFS = {
#     'AUDIENCE': client_id,
#     'CLIENT_ID': client_id,
#     'CLIENT_SECRET': client_secret,
#     'CLAIM_MAPPING': {'first_name': 'given_name',
#                       'last_name': 'family_name',
#                       'email': 'upn'},
#     'GROUPS_CLAIM': 'roles',
#     'MIRROR_GROUPS': True,
#     'USERNAME_CLAIM': 'upn',
#     'TENANT_ID': tenant_id,
#     'RELYING_PARTY_ID': client_id,
# }

#
# Custom configurations
#

APP_NAME = env('APP_NAME', 'PSM')
APP_EMAIL = env('APP_EMAIL', 'no-reply@localhost')
SITE_HEADER = env('SITE_HEADER', 'Project System')
INDEX_TITLE = env('INDEX_TITLE', 'Project System')

ADMINS = (
    (APP_NAME, APP_EMAIL)
)

from .settings_emails import *

# Default login https://docs.djangoproject.com/en/4.0/ref/settings/#login-url
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# django_project/settings.py
EMAIL_ENV = env("EMAIL_ENV", "file")
if EMAIL_ENV == "smtp":
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
    EMAIL_SUBJECT_PREFIX="[PSM-DEV] "

#ckeditor 
# CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'Custom',
#         'toolbar_Custom': [
#             ['Bold', 'Italic', 'Underline', 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'RemoveFormat', 'Source']
#         ],
#         'removePlugins': 'toolbar',
#         'toolbarCanCollapse' : True,     
#         'width': 700,
#     },
# }
# django-richtextfield
#         'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link'
# DJRICHTEXTFIELD_CONFIG = {
#     'js': ['//cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js'],
#     'init_template': 'djrichtextfield/init/tinymce.js',
#     # 'settings': {  #TinyMCE
#     #     'menubar': False,
#     #     'plugins': 'link image',
#     #     'toolbar': 'bold italic | link image | removeformat',
#     #     'width': 700
#     # },
#     'settings': {  # CKEditor
#         'toolbar': [
#             {'items': ['Format', '-', 'Bold', 'Italic', '-',
#                     'RemoveFormat']},
#             {'items': ['Link', 'Unlink', 'Image', 'Table']},
#             {'items': ['Source']}
#         ],
#         'format_tags': 'p;h1;h2;h3',
#         'width': 700
#     }    
# }
