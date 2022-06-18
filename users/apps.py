from django.apps import AppConfig
from django.db.models.signals import pre_save
from django.db import connection
from django.conf import settings

class UsersConfig(AppConfig):
    name = 'users'

# https://docs.djangoproject.com/en/4.0/ref/applications/#django.apps.AppConfig.ready
# https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html

    def ready(self):
        import users.signals

        if settings.SCHEDULER:
            from . import scheduler
            all_tables = connection.introspection.table_names()
            if 'django_apscheduler_djangojob' in all_tables:
                scheduler.start()