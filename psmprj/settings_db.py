# prsmprj/settings_db.py
# DB settings

from . import env
from django.conf import settings

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
                            'sqlite:///%s/db.sqlite3' % settings.BASE_DIR,
                            conn_max_age=env.int('CONN_MAX_AGE', 600)),

    }

# https://django-dbbackup.readthedocs.io/en/master/databases.html
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location':  env("DBBACKUP_LOCATION", settings.BASE_DIR + "/backup")}
# DBBACKUP_CONNECTORS = {
#     'default': {
#         'USER': env("POSTGRES_USER", 'postgres'), 
#         'PASSWORD': env("POSTGRES_PASSWORD", "postgres"),
#         'HOST': '127.0.0.1', 
#     }
# }

