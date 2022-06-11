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
