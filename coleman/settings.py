"""
Django settings for coleman project.

Generated by 'django-admin startproject' using Django.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from . import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', 'here is secret key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)

# Disable admin
ADMIN = env.bool('DJANGO_ADMIN', True)

ALLOWED_HOSTS = [ '*' ]


# Application definition

INSTALLED_APPS = [
#    'jazzmin',
    # 'mtasks.apps.MtasksConfig',
    # 'partner',
    'common',
    'psm',
    'sap',
    'reports',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'import_export',
    'django_admin_listfilter_dropdown',
    'adminfilters',
    # 'django_tables2',
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

ROOT_URLCONF = 'coleman.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates'],
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

WSGI_APPLICATION = 'coleman.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

#
# Database config is passed in environment variable DATABASE_URL
# as string connection like postgresql://dcoleman:postgres@localhost/dcoleman_dev,
# otherwise the default SQLite database below is used.
# See more options at https://github.com/kennethreitz/dj-database-url
#
DATABASES = {
    'default': env.dj_db_url('DATABASE_URL',
                             'sqlite:///%s/db.sqlite3' % BASE_DIR,
                             conn_max_age=env.int('CONN_MAX_AGE', 600)),

# postgresql
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'dbtest', 
    #     'USER': 'postgres', 
    #     'PASSWORD': '1234',
    #     'HOST': '127.0.0.1', 
    #     'PORT': '5432',
    # }
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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = env('LANGUAGE_CODE', 'en-us')

TIME_ZONE = env('TIME_ZONE', 'America/Los_Angeles')

USE_I18N = True
USE_L10N = True
USE_TZ = True


from django.conf.locale.es import formats as es_formats
es_formats.DATETIME_FORMAT = 'd M Y, H:i'
es_formats.DATE_FORMAT = 'd M, Y'


from django.conf.locale.en import formats as en_formats
#en_formats.DATETIME_FORMAT = 'M d Y, H:i'
# en_formats.DATE_FORMAT = 'M d, Y'
en_formats.DATETIME_FORMAT = 'm/d/y g:i a'
en_formats.DATE_FORMAT = 'Y-m-d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR + '/static/'

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

# export/import
#IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'import '

# AzureAD SSO
AUTHENTICATION_BACKENDS = [
#    'django_auth_adfs.backend.AdfsAuthCodeBackend',
#    'microsoft_auth.backends.MicrosoftAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend' # if you also want to use Django's authentication
    # I recommend keeping this with at least one database superuser in case of unable to use others
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
SITE_HEADER = env('SITE_HEADER', 'PSM')
INDEX_TITLE = env('INDEX_TITLE', 'Task Management')

ADMINS = (
    (APP_NAME, APP_EMAIL)
)

from .settings_emails import *

# django_project/settings.py
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# django_project/settings.py
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR + '/sent_emails'

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