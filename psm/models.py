import enum
import logging
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from common.models import CBU, Div, Dept, Team, ExtendUser
from sap.models import WBS

from coleman.utils.mail import send_mail_async as send_mail
from hashlib import sha1

from datetime import date


logger = logging.getLogger(__name__)

number_tr = _("number")

#for year input, validation
import datetime
def year_choices():
    return [(r,r) for r in range(2020, datetime.date.today().year+1)]
def current_year():
    return datetime.date.today().year
def max_value_current_year(value):
    return MaxValueValidator(current_year()+1)(value)
def max_value_program_year(value):
    return MaxValueValidator(current_year()+5)(value)

# Fields used to create an index in the DB and sort the Projects in the Admin
Project_PRIORITY_FIELDS = ('state', 'CBU', '-priority', '-lstrpt')

class State(enum.Enum):
    """
    Status of completion of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    BACKLOG = '00-backlog'
    TO_DO = '10-to-do'
    DOING = '20-doing'
    HOLD = '30-on-hold'
    DONE = '50-done'
    CANCEL = '90-cancel'


class Priority(enum.Enum):
    """
    The priority of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    LOW = '00-low'
    NORMAL = '10-normal'
    HIGH = '20-high'
    CRITICAL = '30-critical'

class Status(enum.Enum):
    NA = '00-notApplicable'
    GREEN = '10-green'
    YELLOW = '20-yellow'
    RED = '20-red'
    COMPLETED = '90-completed'

class PrjType(enum.Enum):
    """
    The priority of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    MAJOR = '00-Major'
    SMALL = '10-Small'
    ENH = '20-Enhancement'
    UNC = '30-Unclassifed'


class Strategy(models.Model):
    class Meta:
        verbose_name = _("Strategy")
        verbose_name_plural = _("Strategies")    
        
    name   = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    def __str__(self):
        return self.name

    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="strategy_created", null=True, on_delete=models.SET_NULL)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

class Program(models.Model):
    class Meta:
        verbose_name = _("Program")
        verbose_name_plural = _("Programs")    

    STATUS = (
        (Status.GREEN.value, _('No Risk')),
        (Status.YELLOW.value, _('Low Risk')),
        (Status.RED.value, _('High Risk')),
        (Status.NA.value, _('Not evaluated')),
    )

    name = models.CharField(max_length=200, blank=True, null=True)
    startyr = models.PositiveIntegerField(_("Starting year"), default=current_year(), validators=[MinValueValidator(2020), max_value_current_year])
    endyr = models.PositiveIntegerField(_("Ending year"), default=current_year(), validators=[MinValueValidator(2020), max_value_program_year])
    lead = models.ForeignKey(ExtendUser, verbose_name=_('Program lead'), on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    description = models.TextField(null=True, blank=True)

    status_r = models.CharField(_("Risk"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    risk_desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# checklist
class CheckItem(models.Model):
    name = models.CharField(_("name"), default="check item...", max_length=200, db_index=True)
    desc = models.CharField(_("description"), max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.name


class ProjectManager(models.Manager):

    def others(self, pk, **kwargs):
        """
        Return queryset with all objects
        excluding the one with the "pk" passed, but
        applying the filters passed in "kwargs".
        """
        return self.exclude(pk=pk).filter(**kwargs)

# -	간혹 프로젝트 주관하는 부서와 달리 협조하는 부서가 Budget 을 받아서 독립된 Schedule 로 진행하는
#  “Collaboration project”있습니다. 이런 경우도 관리가 되면 좋은데..
#  Sub-project? 정도로 해서 서로 연동이 되게 해서 부서별로 PM 및 일정 등을 관리 할수 있으면 좋을 것 같습니다. 
# # 나중에 팀 실적이나 담당자 실적에도 중요한 사항들이구요.

class Project(models.Model):
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    STATES = (
        (State.BACKLOG.value, _('Backlog')),
        (State.TO_DO.value, _('To Do')),
        (State.DOING.value, _('Doing')),
        (State.HOLD.value, _('Blocked')),
        (State.DONE.value, _('Done')),
        (State.CANCEL.value, _('Canceled'))
    )

    PRIORITIES = (
        (Priority.LOW.value, _('Low')),
        (Priority.NORMAL.value, _('Normal')),
        (Priority.HIGH.value, _('High')),
        (Priority.CRITICAL.value, _('Critical')),
    )

    STATUS = (
        (Status.GREEN.value, _('Good')),
        (Status.YELLOW.value, _('Issue')),
        (Status.RED.value, _('Roadblock')),
        (Status.COMPLETED.value, _('Completed')),
        (Status.NA.value, _('Not started')),
    )

    PRJTYPE = (
        (PrjType.MAJOR.value, _('Major')),
        (PrjType.SMALL.value, _('Small')),
        (PrjType.ENH.value, _('Enhancement')),
        (PrjType.UNC.value, _('Unclassified')),
    )

 #   id = models.TextField(blank=True)
    title = models.CharField(_("title"), max_length=200)
    type = models.CharField(_("type"), max_length=20, choices=PRJTYPE, default=PrjType.UNC.value)
    year = models.PositiveIntegerField(_("Year"), default=current_year(), validators=[MinValueValidator(2020), max_value_current_year])
    strategy = models.ForeignKey(Strategy, blank=True, null=True, on_delete=models.PROTECT)
    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.PROTECT)
    is_internal = models.BooleanField(_("Internal project"), default=False)

    CBU = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)
    CBUpm = models.ForeignKey(ExtendUser, related_name='cbu_pm', verbose_name=_('CBU PM'), on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.PROTECT)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.PROTECT)
    div = models.ForeignKey(Div, blank=True, null=True, on_delete=models.PROTECT)

    description = models.TextField(_("description"), max_length=2000, null=True, blank=True)

    status_o = models.CharField(_("status overall"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_t = models.CharField(_("status schedule"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_b = models.CharField(_("status budget"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_s = models.CharField(_("status scope"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    resolution = models.TextField(_("PM Memo"), max_length=2000, null=True, blank=True)
    #settings.AUTH_USER_MODEL
    user = models.ForeignKey(ExtendUser, related_name='project_manager', verbose_name=_('HAEA PM'),
                             on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(_("state"), max_length=20, choices=STATES, default=State.TO_DO.value)
    complete = models.IntegerField(_("complete%"), default=0)
    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)

    est_cost = models.DecimalField(_("Est. cost"), decimal_places=0, max_digits=12, blank=True, null=True)
    app_budg = models.DecimalField(_("Approved budget"), decimal_places=0, max_digits=12, blank=True, null=True)
    wbs = models.ForeignKey(WBS, blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('WBS (SAP)'))
    es = models.CharField(_("ES#"), blank=True, null=True, max_length=30)
    lstrpt = models.DateField(_("last report"), null=True, blank=True)

    p_pre_planning = models.DateField(_("planned pre-planning start"), null=True, blank=True)
    p_kickoff = models.DateField(_("planned kick-off date"), null=True, blank=True)
    p_design_b = models.DateField(_("planned design start"), null=True, blank=True)
    p_design_e = models.DateField(_("planned design end"), null=True, blank=True)
    p_develop_b = models.DateField(_("planned develop start"), null=True, blank=True)
    p_develop_e = models.DateField(_("planned develop end"), null=True, blank=True)
    p_uat_b = models.DateField(_("planned UAT start"), null=True, blank=True)
    p_uat_e = models.DateField(_("planned UAT end"), null=True, blank=True)
    p_launch = models.DateField(_("planned launch"), null=True, blank=True)
    p_close = models.DateField(_("planned closing"), null=True, blank=True)

    a_pre_planning = models.DateField(_("actual pre-planning start"), null=True, blank=True)
    a_kickoff = models.DateField(_("actual kick-off date"), null=True, blank=True)
    a_design_b = models.DateField(_("actual design start"), null=True, blank=True)
    a_design_e = models.DateField(_("actual design end"), null=True, blank=True)
    a_develoa_b = models.DateField(_("actual develop start"), null=True, blank=True)
    a_develoa_e = models.DateField(_("actual develop end"), null=True, blank=True)
    a_uat_b = models.DateField(_("actual UAT start"), null=True, blank=True)
    a_uat_e = models.DateField(_("actual UAT end"), null=True, blank=True)
    a_launch = models.DateField(_("actual launch"), null=True, blank=True)
    a_close = models.DateField(_("actual closing"), null=True, blank=True)

    ssg_sec = models.BooleanField(_("Security Reviewed?"), default=False)
    ssg_inf = models.BooleanField(_("Infra Architecture Reviewed?"), default=False)


    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prj_created_by', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    attachment=models.FileField(_("attachment"), upload_to='attachments', null=True, blank=True)

    objects = ProjectManager()

    class Meta:
        indexes = [
            models.Index(fields=Project_PRIORITY_FIELDS, name='mProjects_Project_priority_idx'),
        ]

    def __str__(self):
#        return "[%s] %s" % (self.number, self.title)
#        return "[%s] %s" % (f'{self.created_at.strftime("%y")}-{"{:04d}".format(self.pk)}', self.title)
        return "[%s] %s" % (f'{self.year % 100}-{"{:04d}".format(self.pk)}', self.title)


    @property
    def PJcode(self) -> str:
#        return "{:08d}".format(self.pk)
#       yy-serial
#        return f'{self.created_at.strftime("%y")}-{"{:04d}".format(self.pk)}'
       return f'{self.year % 100}-{"{:04d}".format(self.pk)}'


    def save(self, *args, **kwargs):
        send_email = self.pk is None
        if not send_email and self.CBU:
            old_Project_data = Project.objects.get(pk=self.pk)
            if old_Project_data.CBU != self.CBU:
                send_email = True
        super().save(*args, **kwargs)
        if send_email:
            # Emails are sent if the order is new
            # or the CBU has changed
            self.send_new_Project_email()

    def clean(self):
        validation_errors = {}
        title = self.title.strip() if self.title else self.title
        if self.CBU:
            if Project.objects \
                    .others(self.pk, title=title, CBU=self.CBU) \
                    .exclude(state__in=(State.DONE.value, State.CANCEL.value)) \
                    .exists():
                validation_errors['title'] = _('Open Project with this title and CBU already exists.')
        else:
            if Project.objects \
                    .others(self.pk, title=title, CBU=None) \
                    .exclude(state__in=(State.DONE.value, State.CANCEL.value)) \
                    .exists():
                validation_errors['title'] = _('Open Project with this title and no CBU already exists.')

        # Add more validations HERE

        if len(validation_errors):
            raise ValidationError(validation_errors)

    def send_new_Project_email(self):
        """
        Override with a custom email
        """
        emails_to = []
        if settings.PROJECT_SEND_EMAILS_TO_CBUS and self.CBU and self.CBU.email:
            emails_to.append(self.CBU.email)
        if settings.PROJECT_SEND_EMAILS_TO_ASSIGNED and self.user and self.user.email:
            emails_to.append(self.user.email)
        if len(emails_to):
            logger.info("[Project #%s] Sending Project creation email to: %s", self.number, emails_to)
            vals = {
                "id": self.number,
                "user": str(self.user) if self.user else '(Not assigned yet)',
                "title": self.title,
                "description": self.description or '-',
                "sign": settings.SITE_HEADER,
            }
            if settings.ProjectS_VIEWER_ENABLED:
                email_template = settings.MProjectS_EMAIL_WITH_URL
                vals["url"] = self.get_Projects_viewer_url()
            else:
                email_template = settings.MProjectS_EMAIL_WITHOUT_URL
            try:
                send_mail(
                    '[{app}] [#{id}] New Project Created'.format(app=settings.APP_NAME, id=self.number),
                    email_template.format(**vals),
                    settings.APP_EMAIL,
                    emails_to,
                )
            except Exception as e:
                logger.warning("[Project #%s] Error trying to send the Project creation email - %s: %s",
                               self.number, e.__class__.__name__, str(e))

    def get_Projects_viewer_url(self):
        """
        Verification token added to the Projects Viewer URL so each one
        sent through email cannot be used to change the order number and
        access to other orders.

        It uses as input a salt code configured and the ID number.

        See: coleman/settings_emails.py
             https://github.com/mrsarm/tornado-dcoleman-mProjects-viewer
        """
        salt = settings.ProjectS_VIEWER_HASH_SALT
        if not settings.DEBUG and salt == '1two3':
            logger.warning("Insecure salt code used to send email orders, do NOT use it in PRODUCTION")
        # created_at_as_iso = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # This ISO format is the same used
                                                                                # used by the REST serializer
        token = "{}-{}".format(salt, self.pk)                                   # SHA-1 is enough secure for
        token = sha1(token.encode('utf-8')).hexdigest()                         # this purpose (SHA-2 is too long)
        return settings.ProjectS_VIEWER_ENDPOINT.format(number=self.number, token=token)


class Item(models.Model):
    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Check List")

    Project = models.ForeignKey(Project, on_delete=models.CASCADE)
    checkitem = models.ForeignKey(CheckItem, blank=True, null=True, on_delete=models.PROTECT)
    item_description = models.CharField(_("description"), max_length=200, blank=True)
    is_done = models.BooleanField(_("done?"), default=False)

    def __str__(self):
        return self.item_description
