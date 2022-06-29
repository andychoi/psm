
Install django-extensions from https://github.com/django-extensions/django-extensions/blob/master/docs/index.rst
----------------------------------------------
 pip install django-extensions

 jupyter notebook --generate-config

 https://www.nathantsoi.com/blog/run-jupyter-notebook-behind-a-nginx-reverse-proxy-subpath/index.html


Change your settings file to include 'django-extensions'
----------------------------------------------
 INSTALLED_APPS += ['django_extensions']

Run your Django server like this:
----------------------------------------------
python manage.py shell_plus --notebook

alter to suit, and run this in your first cell
----------------------------------------------
import os, sys
PWD = os.getenv('PWD')
os.chdir(PWD)
sys.path.insert(0, os.getenv('PWD'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings.py")
import django
django.setup()

Now you should be able to import your django models etc. eg:
----------------------------------------------
from app.models import Foobar
Foobar.objects.all()


NOTEBOOK_ARGUMENTS = [
    # exposes IP and port
    '--ip=0.0.0.0',
    '--port=8888',
    # disables the browser
    '--no-browser',
]

## NGINX and Django/Notebook

The server I want to run Jupyter on has some other apps running on an nginx server, so I'll configure Jupyter to at the path /groot
First, generate the Jupyter config with:

    jupyter notebook --generate-config

Generate a sha1 sum of the password you want to use, in an ipython shell:

    from notebook.auth import passwd; passwd()
Update the config generated in the --generate-config command

    c.NotebookApp.allow_origin = '*'
    c.NotebookApp.base_url = '/groot'
    c.NotebookApp.default_url = '/groot/tree/jupyter'
    c.NotebookApp.password = '[put generated entire password phrase here...]'
    c.NotebookApp.port = 8888
    c.NotebookApp.open_browser = False

NGINX
=====
In the nginx http block, create an upstream:

upstream upstream_groot {
  server localhost:8888;
  keepalive 32;
}

In your nginx server block, set:

    location = /groot {
      rewrite ^/(.*)$ $1/ permanent;
    }
    location /groot {
      error_page 403 = @proxy_groot;
      deny 127.0.0.1;
      allow all;
      # set a webroot, if there is one
      root /some-webroot;
      try_files $uri @proxy_groot;
    }
    location @proxy_groot {
      #rewrite /groot(.*) $1  break;
      proxy_read_timeout 300s;
      proxy_pass http://upstream_groot;
      # pass some extra stuff to the backend
      proxy_set_header Host $host;
      proxy_set_header X-Real-Ip $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location ~ /groot/api/kernels/ {
            proxy_pass            http://upstream_groot;
            proxy_set_header      Host $host;
            # websocket support
            proxy_http_version    1.1;
            proxy_set_header      Upgrade "websocket";
            proxy_set_header      Connection "Upgrade";
            proxy_read_timeout    86400;
        }
    location ~ /groot/terminals/ {
            proxy_pass            http://upstream_groot;
            proxy_set_header      Host $host;
            # websocket support
            proxy_http_version    1.1;
            proxy_set_header      Upgrade "websocket";
            proxy_set_header      Connection "Upgrade";
            proxy_read_timeout    86400;
    }


## Run notebook in daemon

Place the script commands you wish to run in /usr/bin/myscript.

Remember to make the script executable with chmod +x.

Create the following file:

/etc/systemd/system/my.service

[Unit]
Description=My Notebook script
After=network.target

[Service]
Type=simple
User=user1
Group=group1
ExecStart=/usr/bin/myscript
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=default.target

Reload all systemd service files: **systemctl daemon-reload**

Check that it is working by starting the service with **systemctl start my**.


#### https://www.golinuxcloud.com/run-systemd-service-specific-user-group-linux/
[root@centos-8 ~]# id deepak
uid=1000(deepak) gid=1000(deepak) groups=1000(deepak),1001(admin)



