import ast
import logging
import datetime
from django.core.validators import validate_email, MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from common.models import CBU, Div, Dept, Team, Status, STATUS, PrjType, PRJTYPE, State, STATES, Phase, PHASE, Priority, PRIORITIES, State3, STATE3, WBS
from users.models import Profile

from psmprj.utils.mail import send_mail_async as send_mail, split_combined_addresses
from hashlib import sha1


import markdown2

logger = logging.getLogger(__name__)

number_tr = _("number")

from datetime import date
#for year input, validation
import datetime
def year_choices():
    return [(r,r) for r in range(2020, datetime.date.today().year+1)]
def current_year():
    return datetime.date.today().year
def min_year():
    return datetime.date.today().year - 4
def max_value_current_year(value):
    return MaxValueValidator(current_year()+1)(value)
def max_value_program_year(value):
    return MaxValueValidator(current_year()+5)(value)


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

    name = models.CharField(max_length=200, blank=True, null=True)
    startyr = models.PositiveIntegerField(_("Starting year"), default=current_year(), validators=[MinValueValidator(2018), max_value_current_year])
    endyr = models.PositiveIntegerField(_("Ending year"), default=current_year(), validators=[MinValueValidator(2018), max_value_program_year])
    lead = models.ForeignKey(Profile, verbose_name=_('Program lead'), on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(_("Is active?"), default=True)
    description = models.TextField(null=True, blank=True)

    status_r = models.CharField(_("Risk"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    risk_desc = models.TextField(null=True, blank=True)

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
# TODO : GMDM, SSG

# Fields used to create an index in the DB and sort the Projects in the Admin
Project_PRIORITY_FIELDS = ('state', '-priority', '-lstrpt')

class Project(models.Model):
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        indexes = [
            models.Index(fields=Project_PRIORITY_FIELDS, name='mProjects_Project_priority_idx'),
        ]

    code = models.CharField(_("Code"), max_length=10, null=True, blank=True) 

    title = models.CharField(_("title"), max_length=200)
    type = models.CharField(_("type"), max_length=20, choices=PRJTYPE, default=PrjType.UNC.value)
    year = models.PositiveIntegerField(_("Year"), default=current_year(), validators=[MinValueValidator(2014), max_value_current_year])
    strategy = models.ManyToManyField(Strategy, blank=True, null=True, related_name="projects")
    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.PROTECT)
    is_internal = models.BooleanField(_("Internal project"), default=False)
    is_agile = models.BooleanField(_("Agile project"), default=False)
    is_unplanned = models.BooleanField(_("Unplanned project"), default=False)

    CBUs  = models.ManyToManyField(CBU, blank=True, null=True, related_name="projects")
    CBUpm = models.ForeignKey(Profile, related_name='cbu_pm', verbose_name=_('CBU PM'), on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.PROTECT)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.PROTECT)
    # div = models.ForeignKey(Div, blank=True, null=True, on_delete=models.PROTECT)

    description = models.TextField(_("description"), max_length=2000, null=True, blank=True)

    status_o = models.CharField(_("status overall"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_t = models.CharField(_("status schedule"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_b = models.CharField(_("status budget"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_s = models.CharField(_("status scope"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    resolution = models.TextField(_("PM Memo"), max_length=2000, null=True, blank=True)
    #settings.AUTH_USER_MODEL - user directory...
    pm = models.ForeignKey(Profile, related_name='project_manager', verbose_name=_('HAEA PM'),
                           on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(_("state"), max_length=20, choices=STATES, default=State.TO_DO.value)
    phase = models.CharField(_("Phase"), max_length=20, choices=PHASE, default=Phase.PRE_PLAN.value)
    progress = models.SmallIntegerField(_("complete%"), default=0)
    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)

    est_cost = models.DecimalField(_("Est. cost"), decimal_places=0, max_digits=12, blank=True, null=True)
    app_budg = models.DecimalField(_("Approved budget"), decimal_places=0, max_digits=12, blank=True, null=True)
    wbs = models.ForeignKey(WBS, blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('WBS (SAP)'))
    es = models.CharField(_("ES#"), blank=True, null=True, max_length=30)
    ref = models.CharField(_("Reference"), blank=True, null=True, max_length=30)
    lstrpt = models.DateField(_("last report"), null=True, blank=True)

    p_ideation   = models.DateField(_("Planned Ideation start"), null=True, blank=True, default=date.today)
    p_plan_b = models.DateField(_("planned planning start"), null=True, blank=False, default=date.today)
    p_plan_e = models.DateField(_("planned planning end"), null=True, blank=True)
    p_kickoff = models.DateField(_("planned kick-off date"), null=True, blank=False, default=date.today)
    p_design_b = models.DateField(_("planned design start"), null=True, blank=True)
    p_design_e = models.DateField(_("planned design end"), null=True, blank=True)
    p_dev_b = models.DateField(_("planned develop start"), null=True, blank=True)
    p_dev_e = models.DateField(_("planned develop end"), null=True, blank=True)
    p_uat_b = models.DateField(_("planned UAT start"), null=True, blank=True)
    p_uat_e = models.DateField(_("planned UAT end"), null=True, blank=True)
    p_launch = models.DateField(_("planned launch"), null=True, blank=False, default=date.today)
    p_close = models.DateField(_("planned closing"), null=True, blank=False, default=date.today)

    a_plan_b = models.DateField(_("actual planning start"), null=True, blank=True)
    a_plan_e = models.DateField(_("actual planning end"), null=True, blank=True)
    a_kickoff = models.DateField(_("actual kick-off date"), null=True, blank=True)
    a_design_b = models.DateField(_("actual design start"), null=True, blank=True)
    a_design_e = models.DateField(_("actual design end"), null=True, blank=True)
    a_dev_b = models.DateField(_("actual develop start"), null=True, blank=True)
    a_dev_e = models.DateField(_("actual develop end"), null=True, blank=True)
    a_uat_b = models.DateField(_("actual UAT start"), null=True, blank=True)
    a_uat_e = models.DateField(_("actual UAT end"), null=True, blank=True)
    a_launch = models.DateField(_("actual launch"), null=True, blank=True)
    a_close = models.DateField(_("actual closing"), null=True, blank=True)

    # communication
    email_active = models.BooleanField(_("Mailinglist  Active?"), default=False)
    recipients_to = models.TextField(_("Recipients (to)"), max_length=1000, blank=True, null=True)
    recipients_cc = models.TextField(_("Recipients (cc)"), max_length=1000, blank=True, null=True)

    req_pro = models.CharField(_("Procurement Review Needed?"), max_length=20, choices=STATE3, default='00-TBD', blank=True)
    req_sec = models.CharField(_("Info Security Review Needed?"), max_length=20, choices=STATE3, default='00-TBD', blank=True)
    req_inf = models.CharField(_("Infra Architecure Review Needed?"), max_length=20, choices=STATE3, default='00-TBD', blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prj_created_by', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    attachment=models.FileField(_("attachment"), upload_to='projects', null=True, blank=True)

    # what is this for??
    objects = ProjectManager()

    def __str__(self):
#        return "[%s] %s" % (self.number, self.title)
#        return "[%s] %s" % (f'{self.created_at.strftime("%y")}-{"{:04d}".format(self.pk)}', self.title)    
        return "[%s] %s" % (self.pjcode, self.title)
        # return f'{self.year % 100}-{"{:04d}".format(self.pk)}'

    # @property
    # def div(self):
    #     return self.u_dept.div if (self.u_dept.div) else None

    @property
    def description_md2(self):
        return "<div class='psm-md2'>" + markdown2.markdown(self.description) + "</div>"

    @property
    def pjcode(self) -> str:
#        return "{:08d}".format(self.pk)
#       yy-serial
#        return f'{self.created_at.strftime("%y")}-{"{:04d}".format(self.pk)}'
        if (self.code is None) and (not self.pk is None):
            return f'{self.year % 100}-{"{:04d}".format(self.pk)}'
        else:
            return self.code    #migrated records

    @property
    def CBU_str(self):
        # this is not working... FIXME 
        return " ,".join(p.name for p in self.CBUs.all())

    @property
    def strategy_str(self):
        # this is not working... FIXME 
        return " ,".join(p.name for p in self.strategy.all())

    @property
    def emails_to(self):
        return split_combined_addresses(self.recipients_to)

    @property
    def emails_cc(self):
        return split_combined_addresses(self.recipients_cc)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        # save original values, when model is loaded from database,
        instance._loaded_values = dict(zip(field_names, values))    
        return instance


    def save(self, *args, **kwargs):
        send_email = self.pk is None
        if not send_email and self.CBUs.exists():   #FIXME many-to-many
            old_Project_data = Project.objects.get(pk=self.pk)
            # many-to-many compare FIXME
            if list(old_Project_data.CBUs.all()) != list(self.CBUs.all()):
                send_email = True

        # if self.dept:
        #     self.div = self.dept.div    

        super().save(*args, **kwargs)
        
        if self.code is None:
            self.code = f'{self.year % 100}-{"{:04d}".format(self.pk+2000)}'    #migration upto 1999
            self.save()

        if send_email:
            # Emails are sent to manager/HOD if the order is new
            # or the CBU has changed
            self.send_new_project_email()
    
    # validation logic
    def clean(self):
        validation_errors = {}
        title = self.title.strip() if self.title else self.title

        #FIXME manytomany CBU.all() returns Queryset
        # if self.CBU.all():
        #     if Project.objects \
        #             .others(self.pk, title=title, CBU=self.CBU) \
        #             .exclude(state__in=(State.DONE.value, State.CANCEL.value)) \
        #             .exists():
        #         validation_errors['title'] = _('Open Project with this title and CBU already exists.')
        # else:
        #     if Project.objects \
        #             .others(self.pk, title=title, CBU=None) \
        #             .exclude(state__in=(State.DONE.value, State.CANCEL.value)) \
        #             .exists():
        #         validation_errors['title'] = _('Open Project with this title and no CBU already exists.')

        if self.recipients_to and not self.emails_to:
            validation_errors['title'] = _('Email format is not acceptable in Recipients(to)')
        if self.recipients_cc and not self.emails_cc:
            validation_errors['title'] = _('Email format is not acceptable in Recipients(cc)')

        # Add more validations HERE

        if len(validation_errors):
            raise ValidationError(validation_errors)

    def send_new_project_email(self):
        """
        Override with a custom email
        """
        emails_to = []
        if settings.PROJECT_SEND_EMAILS_TO_CBUS and self.CBUpm and self.CBUpm.email:
            emails_to.append(self.CBUpm.email)
        if settings.PROJECT_SEND_EMAILS_TO_ASSIGNED and self.pm and self.pm.email:
            emails_to.append(self.pm.email)
        if len(emails_to):
            logger.info("[Project #%s] Sending Project creation email to: %s", self.number, emails_to)
            vals = {
                "id": self.number,
                "user": str(self.user) if self.user else '(Not assigned yet)',
                "title": self.title,
                "description": self.description or '-',
                "sign": settings.SITE_HEADER,
            }
            if settings.PSM_VIEWER_ENABLED:
                email_template = settings.PSM_EMAIL_WITH_URL
                vals["url"] = self.get_Projects_viewer_url()
            else:
                email_template = settings.PSM_EMAIL_WITHOUT_URL
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

        See: psmprj/settings_emails.py
             https://github.com/FIXME/tornado-dpsmprj-mProjects-viewer
        """
        salt = settings.PSM_VIEWER_HASH_SALT
        if not settings.DEBUG and salt == '1two3':
            logger.warning("Insecure salt code used to send email orders, do NOT use it in PRODUCTION")
        # created_at_as_iso = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # This ISO format is the same used
                                                                                # used by the REST serializer
        token = "{}-{}".format(salt, self.pk)                                   # SHA-1 is enough secure for
        token = sha1(token.encode('utf-8')).hexdigest()                         # this purpose (SHA-2 is too long)
        return settings.ProjectS_VIEWER_ENDPOINT.format(number=self.number, token=token)

# checklist
class ProjectDeliverableType(models.Model):
    name = models.CharField(_("name"), max_length=200, db_index=True)
    desc = models.CharField(_("description"), max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = _("Deliverable Type")
        verbose_name_plural = _("Deliverable Types")

class ProjectDeliverable(models.Model):
    class Meta:
        verbose_name = _("Project Deliverable")
        verbose_name_plural = _("Project Deliverables")

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    deliverable_type = models.ForeignKey(ProjectDeliverableType, blank=True, null=True, on_delete=models.PROTECT)
    item_description = models.CharField(_("Description"), max_length=200, blank=True)
    deadline = models.DateField(_("Deadline"), null=True, blank=True)

    is_done = models.BooleanField(_("done?"), default=False)

    def __str__(self):
        return self.item_description
