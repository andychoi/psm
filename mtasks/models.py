import enum
import logging

from django.core.exceptions import ValidationError
from django.db import models
# from river.models.fields.state import StateField
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import CBU, State, Priority, PRIORITIES, STATES
from psm.models import Project
from psmprj.utils.mail import send_mail_async as send_mail
from hashlib import sha1
from users.models import Profile

logger = logging.getLogger(__name__)

number_tr = _("number")

# Fields used to create an index in the DB and sort the tasks in the Admin
TASK_PRIORITY_FIELDS = ('state', '-priority', '-deadline')


# class State(enum.Enum):
#     """
#     Status of completion of the task
#     (codes are prefixed with numbers to be easily sorted in the DB).
#     """
#     TO_DO = '00-to-do'
#     IN_PROGRESS = '10-in-progress'
#     BLOCKED = '20-blocked'
#     DONE = '30-done'
#     DISMISSED = '40-dismissed'


# class Priority(enum.Enum):
#     """
#     The priority of the task
#     (codes are prefixed with numbers to be easily sorted in the DB).
#     """
#     LOW = '00-low'
#     NORMAL = '10-normal'
#     HIGH = '20-high'
#     CRITICAL = '30-critical'


class TaskManager(models.Manager):

    def others(self, pk, **kwargs):
        """
        Return queryset with all objects
        excluding the one with the "pk" passed, but
        applying the filters passed in "kwargs".
        """
        return self.exclude(pk=pk).filter(**kwargs)

class TaskType(models.Model):
    class Meta:
        verbose_name = _("Task Type")
        verbose_name_plural = _("Task Types")    
        
    name   = models.CharField(max_length=100, blank=True, null=True, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    def __str__(self):
        return self.name

# custom permission: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/
class Task(models.Model):
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")


    # STATES = (
    #     (State.TO_DO.value, _('To Do')),
    #     (State.IN_PROGRESS.value, _('In Progress')),
    #     (State.BLOCKED.value, _('Blocked')),
    #     (State.DONE.value, _('Done')),
    #     (State.DISMISSED.value, _('Dismissed'))
    # )

    # PRIORITIES = (
    #     (Priority.LOW.value, _('Low')),
    #     (Priority.NORMAL.value, _('Normal')),
    #     (Priority.HIGH.value, _('High')),
    #     (Priority.CRITICAL.value, _('Critical')),
    # )

    ttype = models.ForeignKey(TaskType, verbose_name=_("Task Type"), blank=True, null=True, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, blank=True, null=True, verbose_name=_('related project'), on_delete=models.PROTECT)
    title = models.CharField(_("title"), max_length=200)
    CBU = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)
    description = models.TextField(_("description"), max_length=2000, null=True, blank=True)
    resolution = models.TextField(_("resolution"), max_length=2000, null=True, blank=True)
    deadline = models.DateField(_("deadline"), null=True, blank=True)
    user = models.ForeignKey(Profile, related_name='tasks_assigned', verbose_name=_('assigned to'),
                             on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(_("state"), max_length=20, choices=STATES, default=State.TO_DO.value)
    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='users_created', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    # not compatible with django 4.x
    # wf_state = StateField() #https://django-river.readthedocs.io/en/latest/getting_started.html

    objects = TaskManager()

    class Meta:
        indexes = [
            models.Index(fields=TASK_PRIORITY_FIELDS, name='mtasks_task_priority_idx'),
        ]

        permissions = [
            # ("change_task_status", "Can change the status of tasks"),
            # ("close_task", "Can remove a task by setting its status as closed"),
            ('change_status', 'Change status'),
            # ('assign_task', 'Assign task'),
            # ('close_task', 'Close task'),
        ]        

    def __str__(self):
        return "[%s] %s" % (self.number, self.title)
        
    @property
    def number(self) -> str:
        return "{:08d}".format(self.pk)

#   not working: https://stackoverflow.com/questions/23361057/django-comparing-old-and-new-field-value-before-saving
#   try this
    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        # save original values, when model is loaded from database,
        instance._loaded_values = dict(zip(field_names, values))    
        return instance

    def save(self, *args, **kwargs):
        send_email = self.pk is None
        if not send_email and self.CBU:
            old_task_data = Task.objects.get(pk=self.pk)
            if old_task_data.CBU != self.CBU:
                send_email = True
        super().save(*args, **kwargs)
        if send_email:
            # Emails are sent if the order is new
            # or the CBU has changed
            self.send_new_task_email()

    def clean(self):
        validation_errors = {}
        title = self.title.strip() if self.title else self.title
        ttype = self.ttype
        if self.CBU:
            if Task.objects \
                    .others(self.pk, ttype=ttype, title=title, CBU=self.CBU) \
                    .exclude(state__in=(State.DONE.value, State.DISMISSED.value)) \
                    .exists():
                validation_errors['title'] = _('Open task with this title, task type and CBU already exists.')
        else:
            if Task.objects \
                    .others(self.pk, ttype=ttype, title=title, CBU=None) \
                    .exclude(state__in=(State.DONE.value, State.DISMISSED.value)) \
                    .exists():
                validation_errors['title'] = _('Open task with this title, task type and no CBU already exists.')

        # Add more validations HERE

        if len(validation_errors):
            raise ValidationError(validation_errors)

    def send_new_task_email(self):
        """
        Override with a custom email
        """
        emails_to = []
        if settings.TASKS_SEND_EMAILS_TO_PARTNERS and self.CBU and self.CBU.email:
            emails_to.append(self.CBU.email)
        if settings.TASKS_SEND_EMAILS_TO_ASSIGNED and self.user and self.user.email:
            emails_to.append(self.user.email)
        if len(emails_to):
            logger.info("[Task #%s] Sending task creation email to: %s", self.number, emails_to)
            vals = {
                "id": self.number,
                "user": str(self.user) if self.user else '(Not assigned yet)',
                "title": self.title,
                "description": self.description or '-',
                "sign": settings.SITE_HEADER,
            }
            if settings.TASKS_VIEWER_ENABLED:
                email_template = settings.MTASKS_EMAIL_WITH_URL
                vals["url"] = self.get_tasks_viewer_url()
            else:
                email_template = settings.MTASKS_EMAIL_WITHOUT_URL
            try:
                send_mail(
                    '[{app}] [#{id}] New Task Created'.format(app=settings.APP_NAME, id=self.number),
                    email_template.format(**vals),
                    settings.APP_EMAIL,
                    emails_to,
                )
            except Exception as e:
                logger.warning("[Task #%s] Error trying to send the task creation email - %s: %s",
                               self.number, e.__class__.__name__, str(e))

    def get_tasks_viewer_url(self):
        """
        Verification token added to the Tasks Viewer URL so each one
        sent through email cannot be used to change the order number and
        access to other orders.

        It uses as input a salt code configured and the ID number.

        See: FIXME/settings_emails.py
             https://github.com/FIXME/tornado-dFIXME-mtasks-viewer
        """
        salt = settings.TASKS_VIEWER_HASH_SALT
        if not settings.DEBUG and salt == '1two3':
            logger.warning("Insecure salt code used to send email orders, do NOT use it in PRODUCTION")
        # created_at_as_iso = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # This ISO format is the same used
                                                                                # used by the REST serializer
        token = "{}-{}".format(salt, self.pk)                                   # SHA-1 is enough secure for
        token = sha1(token.encode('utf-8')).hexdigest()                         # this purpose (SHA-2 is too long)
        return settings.TASKS_VIEWER_ENDPOINT.format(number=self.number, token=token)


class TaskItem(models.Model):
    class Meta:
        verbose_name = _("Task Item")
        verbose_name_plural = _("Task Items")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    item_description = models.CharField(_("description"), max_length=200)
    is_done = models.BooleanField(_("done?"), default=False)

    def __str__(self):
        return self.item_description
