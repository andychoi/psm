#
# Emails configuration and templates used when a task order is created, CUSTOMIZE...
#
# django_project/settings_emails.py
import os
from . import env

# Use 'django.core.mail.backends.console.EmailBackend'
# to use a fake backend that prints out the email
# in the standard output instead of sending the emails
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMAIL_ENV = env("EMAIL_ENV", "file")
if EMAIL_ENV == "smtp":
    EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
else:
    EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.filebased.EmailBackend')
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
    
EMAIL_TIMEOUT = 3      # seconds
EMAIL_HOST = env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', 'YOUREMAIL@localhost')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', 'PASS')

DEFAULT_FROM_EMAIL=env('DEFAULT_FROM_EMAIL', 'no-reply-psm@localhost')
EMAIL_TEST_RECEIVER=env('EMAIL_TEST_RECEIVER', 'system-sender@localhost')

# Project App related settings and templates
EMAIL_DEV = env.bool('EMAIL_DEV', True)
if EMAIL_DEV:
    EMAIL_SUBJECT_PREFIX="[PSM-Testing] "
else:
    EMAIL_SUBJECT_PREFIX="[PSM] "

PROJECT_SEND_EMAILS_TO_ASSIGNED = env.bool('PROJECT_SEND_EMAILS_TO_ASSIGNED', True)
PROJECT_SEND_EMAILS_TO_CBUS = env.bool('PROJECT_SEND_EMAILS_TO_CBUS', False)

PSM_EMAIL_WITHOUT_URL = '''\
New project #{id} created.

Title:
{title}

Assigned:
{PM}

CBU:
{CBU}

CBU PM:
{CBU_PM}

Description:
{description}

Please note: Do NOT reply to this email. This email is sent from an unattended mailbox.
Replies will not be read.

---
{sign}
'''


PSM_EMAIL_WITH_URL = '''\
New project #{id} created.

Title:
{title}

Assigned:
{user}

Description:
{description}

Order URL:
{url}

Please note: Do NOT reply to this email. This email is sent from an unattended mailbox.
Replies will not be read.

---
{sign}
'''

# Task App related 
TASKS_SEND_EMAILS_TO_ASSIGNED = env.bool('TASKS_SEND_EMAILS_TO_ASSIGNED', True)
TASKS_SEND_EMAILS_TO_PARTNERS = env.bool('TASKS_SEND_EMAILS_TO_PARTNERS', False)

# Enables the Tornado PSM Viewer (it will send emails with the order URL)
# Check: https://github.com/FIXME/tornado-dpsmprj-mtasks-viewer
TASKS_VIEWER_ENABLED = env.bool('TASKS_VIEWER_ENABLED', False)
TASKS_VIEWER_HASH_SALT = env('TASKS_VIEWER_HASH_SALT', '1two3')   # REPLACE in production !!!
TASKS_VIEWER_ENDPOINT = env('TASKS_VIEWER_ENDPOINT', 'http://localhost:8888/{number}?t={token}')

MTASKS_EMAIL_WITHOUT_URL = '''\
New task #{id} created.

Title:
{title}

Assigned:
{user}

Description:
{description}

Please note: Do NOT reply to this email. This email is sent from an unattended mailbox.
Replies will not be read.

---
{sign}
'''


MTASKS_EMAIL_WITH_URL = '''\
New task #{id} created.

Title:
{title}

Assigned:
{user}

Description:
{description}

Order URL:
{url}

Please note: Do NOT reply to this email. This email is sent from an unattended mailbox.
Replies will not be read.

---
{sign}
'''