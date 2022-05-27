Django Project Service Management
=================================

PSM: A very simple Project Service Management web app 
*reference to Task Management web app written with **Django Admin**.

Features
--------

* Simple task manager that allows to define a tasks with title,
  CBU (customer, provider...), description, responsible of the task, priority...
* Each task may have items: sub-tasks to be done.
* The built-in Django *Authentication and Authorization* system
  to manage users and groups, login, etc.
* Module `django-adminfilters <https://github.com/FIXME/django-adminfilters>`_
  that allows multiselection searches.
* Send emails when a task is created.
* Basic Rest API configuration (disabled by default, check the ``INSTALLED_APPS`` setting).
* Pytest with some tests as example and code coverage reports configured.
* Docker and Docker Compose configurations 
* Ready to use "production" configurations as reference.

Requirements
------------

Docker, or:
* Python 3.8+ (tested with Python 3.8 and 3.9).
* Django 5.x and other dependencies declared in
  the ``requirements.txt`` file (use virtual environments or containers!).
* A Django compatible database like PostgreSQL (by default uses
  the Python's built-in SQLite database for development purpose).
* Default database is postgresql now.
  database: psmdb
  user: postgres
  create .env file for password: POSTGRES_PASSWORD


Install and Run
---------------

Using Docker, check the section below. Otherwise:

Create a virtual environment and activate it with *(Optional)*::

    $ python3.8 -m venv .venv && source .venv/bin/activate

Install dependencies with::

    $ python -m pip install --upgrade pip wheel
    $ python -m pip install -r requirements.txt

Create the database with::

    $ python manage.py makemigrations
    $ python manage.py makemigrations common psm sap reports mtasks reviews
    $ python manage.py migrate

To create an admin user::

    $ python manage.py createsuperuser

Then run in development mode with::

    $ python manage.py runserver 0.0.0.0:8000

Or you can run with gunicorn::

    $ python -m gunicorn psmprj.wsgi:application --bind 0.0.0.0:8000 --workers 3

Add at the end ``0:5000`` if you want to open the port 5000
instead of the default 8000, and the ``0:`` prefix is to
let Django accepts connection outside localhost (optional).

Or use the following script to startup in "production" mode,
with a uWSGI server::

    $ uwsgi uwsgi.ini


Procfile and Honcho
^^^^^^^^^^^^^^^^^^^

The project also include a `<Procfile>`_, ready to use
in platforms that support it like Heroku, or with
command line tools like `Honcho <https://honcho.readthedocs.io>`_
or Foreman.

Honcho has the advantage of loading the environment variables
from an .env file automatically (see section below). To install
it execute ``pip3 install honcho``. Once installed, to run
the app with Honcho::

    $ honcho start web

There are other shortcuts in the Procfile, like a command to
create both the user and database (you have to provide the
"master" password from the user "postgres" in an env variable)::

    $  POSTGRES_PASSWORD=postgres honcho start createdb

And here is the command to automatically creates an "admin" user
with password "admin1234"::

    $ honcho start createadmin


Docker
------

A reference `<Dockerfile>`_ is provided, and the image published
in `Docker Hub <https://hub.docker.com/r/FIXME/django-psmprj>`_.

Also `<docker-compose.yml>`_ and `<.env.example>`_ files are provided, you can run
all from here, PSM, the viewer app and Postgres.

First, copy the ``.env.example`` file as ``.env`` file, and edit whatever
value you want to::

    $ cp .env.example .env

Then before run for the first time the containers, you have to either
download the images from Docker Hub or build them from the source code. To
build the images from the source code, execute::

    $ docker-compose build

Or to get the images from Docker Hub, execute::

    $ docker-compose pull

Once the images are installed in your local machine, create the containers
and run all of them with::

    $ docker-compose up

The first time it runs some errors about the DB are shown, that's because
you need to create the DB and the structure (tables, indexes), all can
be created in another terminal executing::

    $ docker-compose run django-psmprj-provision

Even a user ``admin`` with password ``admin1234`` is created.

Access the apps and the DB
^^^^^^^^^^^^^^^^^^^^^^^^^^

The URL to access the app is the same than running it with
Python locally: http://localhost:8000/admin/ .

Once created an order, if the id is ``1``, it can be viewed
by the viewer with http://localhost:8888/1?t=porgs .

If you want to then open a `psql` session for the DB from the
containers: ``docker-compose run psql``.

Local persistence
^^^^^^^^^^^^^^^^^

By default a local volume ``django-psmprj_data`` is attached
to the Postgres container so even executing ``docker-compose down``
won't delete the data, but if you want to start from scratch::

    $ docker-compose down
    $ docker volume rm pg-psmprj_data

Add changes in the code
^^^^^^^^^^^^^^^^^^^^^^^

When adding changes in the code, the image needs to be updated::

    $ docker-compose build

Then run again. A script ``docker-build.sh`` with more advance
features and without using docker-compose is also provided
to re-build the image.


Settings
--------

Most settings can be overwritten with environment variables.
For example to overwrite the language translations of the application and
set *debug* options to false::

    $ DEBUG=False LANGUAGE_CODE=es-ar python3 manage.py runserver

Also in development environments an ``.env`` file can be used to setup
the environment variables easily, checkout the `<.env.example>`_ as example.
You can copy the example file and edit the variables you want to change::

   $ cp .env.example .env
   $ vi .env

Some available settings:

* ``DEBUG``: set the Django ``DEBUG`` option. Default ``True``.
* ``TIME_ZONE``: default ``UTC``. Other example: ``America/Buenos_Aires``.
* ``LANGUAGE_CODE``: default ``en-us``. Other example: ``es-ar``.
* ``SITE_HEADER``: Header title of the app. Default to *"PSM - A Simple Task Manager"*.
* ``DATABASE_URL``: Database string connection. Default uses SQLite database. Other
  example: ``postgresql://dpsmprj:postgres@localhost/dpsmprj_dev``.
* More settings like email notifications, check the ``settings.py`` file
  for more details, any variable that is set with ``env('...`` is able
  to be configured using environment variables.

To run in a production environment, check the `<README-production.rst>`_ notes, or
see the official Django documentation.


Access the application
----------------------

Like any Django app developed with Django Admin, enter with: http://localhost:8000/admin


Tests
-----

Tests run with Pytest::

    $ pytest

Or use the Honcho task that also generates a report with
the tests coverage: ``honcho start --no-prefix test``.



Development
-----------

Some tips if you are improving this application.

Translations
^^^^^^^^^^^^

After add to the source code new texts to be translated, in the command
line go to the module folder where the translations were edited, e.g.
the "mtasks" folder, and execute the following replacing ``LANG``
by a valid language code like ``es``::

    $ django-admin makemessages -l LANG

Then go to the *.po* file and add the translations. In the
case of the "mtasks" module with ``es`` language, the file is
located at ``mtasks/locale/es/LC_MESSAGES/django.po``. Finally
execute the following to compile the locales::

    $ django-admin compilemessages


