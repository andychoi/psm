# Misc settings

from . import env

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

# USE_THOUSAND_SEPARATOR = True

DEFAULT_AUTH_GROUP  = env('DEFAULT_AUTH_GROUP', "staff")

MY_DOMAIN = env('MY_DOMAIN', 'abc.local')
MY_CBU = env('MY_CBU', 'MY')
MY_APP_URL = env('MY_APP_URL', 'psm.localhost')
SCHEDULER = env.bool('SCHEDULER', False)

#https://docs.djangoproject.com/en/dev/ref/settings/#data-upload-max-memory-size
DATA_UPLOAD_MAX_MEMORY_SIZE=10*1024*1024
# NGINX Default nginx client_max_body_size = 1MB

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240   #default 1000