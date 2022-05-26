"""
WSGI config for psmprj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application

from psmprj import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmprj.settings")

if settings.STATIC_ENABLE_WSGI_HANDLER:
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
