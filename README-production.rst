Run in production mode
======================

To run in production mode, you must install a WSGI compliant server
like *uWSGI* or *Gunicorn*. Also run a production-ready database like
PostgreSQL or MySQL.

To run the project with uWSGI server at port 8000, and connect
with a Postgres database named ``dpsmprj_dev``
(or other specified in the environment variable ``DATABASE_URL``),
execute::

    $ ./run prod

Before run the first time, install the dependencies with::

    $ pip install -r requirements/requirements-prod.txt

The static resources must served with a HTTP server
like *Nginx* or *Apache HTTP*. To collect all static resources
in the folder ``static/``, execute once::

    $ python manage.py collectstatic

Nginx configuration
-------------------
Nginx default site should be removed.
This is an example of how should looks like a *Nginx* configuration

    server {
        listen      80;
        server_name <server name>;
        access_log  /var/log/nginx/django.access.log;
        error_log   /var/log/nginx/django.error.log;

        root /path/to/project;

        location /static {
            alias /path/to/project/psm/static 
        }

        location / {
            proxy_pass   http://127.0.0.1:8000;
        }

        proxy_cache_valid       200  1d;
        proxy_cache_use_stale   error timeout invalid_header updating
                                http_500 http_502 http_503 http_504;

        proxy_redirect          off;
        proxy_set_header        Host            $host;
        proxy_set_header        X-Real-IP       $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    server {
        listen     443 default ssl;
        server_name  <Nginx_server_name>;

        ## edit the rest of the server{} section to look like this ##
        ssl_certificate     /etc/nginx/cert/nginx-server.crt;
        ssl_certificate_key /etc/nginx/cert/nginx-server.key;
    
        #ssl on;  <- not need for mixed use http,https
        ssl_session_cache  builtin:1000  shared:SSL:10m;
        ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
        ssl_prefer_server_ciphers  on;
        ssl_session_timeout  5m;

        location /static {
            alias /path/to/project/psm/static 
        }

        location / {
            access_log off;
            proxy_pass https://127.0.0.1:8443;
            proxy_http_version 1.1;  
            proxy_connect_timeout 5s;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }
      }

With the above configuration, the Admin interface should be accessible
at http://django-psmprj/admin

If you can't see the Admin page correctly, and the browser console shows
you *403 Forbidden* errors, ensure the system user that runs the Nginx server
has permissions to access to the PSM resources.

Also be sure to have mapped `django-psmprj` in your DNS server, or in the
`/etc/hosts` where you want to access the app::

   echo '127.0.0.1 django-psmprj' | sudo tee -a /etc/hosts


PostgreSQL database
-------------------

If you want to use a PostgreSQL database (recommended), before run
the `migration scripts <https://github.com/FIXME/django-psmprj/#install-and-run>`_
be sure to create the user and the database used by PSM.
In the ``run.sh`` script is used this string connection
as example: ``postgresql://dpsmprj:postgres@localhost/dpsmprj_dev``,
so to create a database ``dpsmprj_dev`` with a user ``dpsmprj`` and a
password ``postgres``, first create the user with::

    $ sudo -u postgres createuser --createdb --no-superuser --no-createrole --pwprompt psmprj

If you are already logged-in as a superuser, you can execute instead the following, within the SQL session:
``CREATE USER dpsmprj;``, and then to be prompted for a password within a ``psql`` session
execute ``\password dpsmprj``.

Then create the database with::

    $ sudo -u postgres psql
    postgres=# CREATE DATABASE psmdb OWNER psmprj;

Another way to create user and database in Postgres is to use
the Procfile task ``createdb``, checkout the section below.


Docker and Procfile
-------------------

**Docker**: ???? to implement ...

**Procfile**: provided in the source code, the ``web``
task allows to launch the webserver, checkout the `<.env.example>`_
file and the `<README.rst>`_ guides of how to use
it with *Honcho*.


##Linux Service

/etc/systemd/system/psm.service
-------------------------------
[Unit]
Description=psm

[Service]
PermissionsStartOnly = true
User=psm
Group=psm
ExecStart=/bin/sh /opt/app/.psm_daemon/run.sh

/opt/app/.psm_daemon/run.sh
---------------------------
cd psm
PIDFILE=psmapp.pid
.venv/bin/gunicorn psmprj.wsgi:application --bind 0.0.0.0:8000 --workers 3 --pid $PIDFILE

Reference
------------
https://bartsimons.me/gunicorn-as-a-systemd-service/



Steps to clear out the history of a git/github repository
---------------------------------------------------------
-- Remove the history from 
rm -rf .git

-- recreate the repos from the current content only
git init
git add .
git commit -m "Initial commit"

-- push to the github remote repos ensuring you overwrite history
git remote add origin git@github.com:<YOUR ACCOUNT>/<YOUR REPOS>.git
git push -u --force origin master


Static files
------------

You can serve static in DEBUG=False using
    $ python manage.py runserver --insecure

https://stackoverflow.com/questions/54566491/why-does-django-not-load-static-files-if-debug-false
Or you may run in DEBUG=False using middleware

    $ pip install whitenoise

Remove old custom permissions
-----------------------------
    $ python manage.py remove_stale_contenttypes --include-stale-apps


Backup & restore plan
---------------------
https://stackoverflow.com/questions/34822002/django-backup-strategy-with-dumpdata-and-migrations

Postgres dumpdata
    $ pg_dump -U $user -Fc $database --exclude-table=django_migrations > path/to/backup-dir/db.dump

Django dumpdata and loaddata
    $ python manage.py dumpdata \
    --exclude auth.permission --exclude contenttypes --exclude admin.LogEntry --exclude sessions \
    --exclude auth.user
    --natural-foreign 
    --natural-foreign --natural-primary
    --format jsonl --indent 2 --output ../db.json

    $ python manage.py loaddata ../db.json

https://markvanlent.dev/2011/05/06/integrityerror-duplicate-key-value-violates-unique-constraint/
As is often the case: once you???ve discovered the cause of the problem, the solution becomes trivial. 
In this case I just had to set the last_value of the sequence to the highest ID in the table.

I chose the quick-and-dirty solution to create a new, empty migration:

    $ python manage.py makemigrations --empty users

Then I added this code to the forwards method:

    if orm.Profile.objects.count():
        highest_number = db.execute('select id from users_profile order by id desc limit 1;')[0][0]
        db.execute('alter sequence users_profile_id_seq restart with %s;' % (highest_number + 1))

I probably could have safely set the sequence to highest number but I choose to increment by one 
just to make sure I didn???t have an off-by-one error. The second line fails if there are no Profile 
so to prevent my tests from failing I check for the existence of Profile explicitly.

After I ran this migration on the production environment, users could create profiles again without triggering an IntegrityError.


OnetoOne field issue
---------------------
Profile.user = models.OneToOneField(User) when django creates User records 
it automatically creates Profiles for these users (probably via post_save). 
So when loaddata starts to import Profiles, each User already has a profile and additional profiles break the constraint.

1) export auth.user into a separate auth_user.json;
    python manage.py dumpdata --indent=4 auth.user auth.group --natural-foreign --natural-primary --output  ../psm_sandbox/auth_user.json

2) export other models:
    python manage.py dumpdata --indent=4 -e sessions -e admin -e contenttypes -e auth.Permission --natural-foreign --natural-primary --output ../psm_sandbox/other_models.json

3) load User records: 
    python manage.py loaddata   ../auth_user.json

4) open ./manage.py shell or shell_plus and delete all the Profiles:
    Profiles.objects.all().delete()
    Profiles.objects.all().count()

5) load the rest of the records:
    python manage.py loaddata ../other_models.json


Django permission 
-----------------
https://testdriven.io/static/images/blog/django/drf-permissions/permissions_execution.png