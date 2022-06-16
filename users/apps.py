from django.apps import AppConfig
from django.db.models.signals import pre_save

class UsersConfig(AppConfig):
    name = 'users'

# https://docs.djangoproject.com/en/4.0/ref/applications/#django.apps.AppConfig.ready
# https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html

    def ready(self):
        import users.signals

        from . import scheduler
        scheduler.start()