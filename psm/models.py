import ast
import sys
import logging
import datetime
# import cffi
from django.core.validators import validate_email, MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib import messages

from common.models import Status, STATUS, PrjType, PRJTYPE, State, STATES, Phase, PHASE, Priority, PRIORITIES, Action3, ACTION3, PrjSize, PRJSIZE
from common.models import CBU, Div, Dept, Team
from common.models import WBS, VERSIONS, Versions
from users.models import Profile, ProfileCBU

from psmprj.utils.mail import send_mail_async as send_mail, split_combined_addresses
from common.dates import previous_business_day
from django.utils.html import mark_safe, escape
from common.utils import md2
from common.proxy import ObjectManager, ProxySuper, ProxyManager
from hashlib import sha1
from sorl.thumbnail import get_thumbnail

#TODO https://docs.djangoproject.com/en/4.0/ref/contrib/postgres/search/
#from django.contrib.postgres.search import SearchQuery


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
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

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

# ----------------------------------------------------------------------------------------------------
class ProjectManager(models.Manager):
    def others(self, pk, **kwargs):
        """
        Return queryset with all objects
        excluding the one with the "pk" passed, and carryfoward but
        applying the filters passed in "kwargs".
        """
        if pk:
            # obj = Project.objects.get(pk=pk)
            return self.exclude(pk=pk).filter(**kwargs)
        else: #new record
            return self.filter(**kwargs)


# Fields used to create an index in the DB and sort the Projects in the Admin
Project_PRIORITY_FIELDS = ('state', '-priority', '-lstrpt')


class Project(models.Model):
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Project")
        indexes = [
            # models.Index(fields=Project_PRIORITY_FIELDS, name='mProjects_Project_priority_idx'),
        ]
        permissions = [ ("access_project_cbu",     "Can access by CBU user)"),
        ]

    code = models.CharField(_("Code"), max_length=18, null=True, blank=True) 
    cf   = models.BooleanField(_("carryforward?"),default=False)

    title = models.CharField(_("title"), max_length=200)
    type = models.CharField(_("type"), max_length=20, choices=PRJTYPE, default=PrjType.ENH.value)
    size = models.CharField(_("Size"), max_length=20, choices=PRJSIZE, default=PrjSize.SML.value)
    year = models.PositiveIntegerField(_("Year"), default=current_year(), validators=[MinValueValidator(2014), max_value_current_year])
    strategy = models.ManyToManyField(Strategy, blank=True)
    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.PROTECT)
    is_internal = models.BooleanField(_("Internal project"), default=False)
    is_agile = models.BooleanField(_("Agile project"), default=False)
    # is_unplanned = models.BooleanField(_("Unplanned project"), default=False)

    CBUs  = models.ManyToManyField(CBU, blank=True)
    CBUpm = models.ForeignKey(Profile, related_name='cbu_pm', verbose_name=_('CBU PM'), on_delete=models.PROTECT, null=True, blank=True)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.SET_NULL)
    # div = models.ForeignKey(Div, blank=True, null=True, on_delete=models.PROTECT)

    description = models.TextField(_("description"), max_length=2000, null=True, blank=True)
    objective   = models.TextField(_("Objectives"),  max_length=2000, null=True, blank=True)

    ref_plan    = models.ForeignKey("ProjectRequest", on_delete=models.SET_NULL, null=True, blank=True)

    status_o = models.CharField(_("Overall Health"), max_length=20, choices=STATUS, default=Status.NA.value)
    status_t = models.CharField(_("Schedule status"), max_length=20, choices=STATUS, default=Status.NA.value)
    status_b = models.CharField(_("Budget status"), max_length=20, choices=STATUS, default=Status.NA.value)
    status_s = models.CharField(_("Scope status"), max_length=20, choices=STATUS, default=Status.NA.value)
    pm_memo = models.TextField(_("PM Memo"), max_length=2000, null=True, blank=True)
    #settings.AUTH_USER_MODEL - user directory...
    pm = models.ForeignKey(Profile, related_name='project_manager', verbose_name=_('PM'),
                           on_delete=models.PROTECT, null=True, blank=True)
    state = models.CharField(_("state"), max_length=20, choices=STATES, default=State.TODO.value)
    phase = models.CharField(_("Phase"), max_length=20, choices=PHASE, default=Phase.PRE_PLAN.value)
    progress = models.PositiveSmallIntegerField(_("complete%"), default=0)
    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)

    # PROBLEM with decimal type in pandas df, pivot ...
    est_cost = models.DecimalField(_("Est. cost"), decimal_places=0, max_digits=12, blank=True, null=True)
    budget = models.DecimalField(_("Approved budget"), decimal_places=0, max_digits=12, blank=True, null=True)
    # est_cost = models.FloatField(_("Est. cost"), decimal_places=0, max_digits=12, blank=True, null=True)
    # budget = models.FloatField(_("Approved budget"), decimal_places=0, max_digits=12, blank=True, null=True)
    wbs = models.ForeignKey(WBS, blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('WBS (SAP)'))
    es = models.CharField(_("ES#"), blank=True, null=True, max_length=100)
    ref = models.CharField(_("Reference"), blank=True, null=True, max_length=100)
    lstrpt = models.DateField(_("last report"), null=True, blank=True)

    p_ideation   = models.DateField(_("Planned Ideation start"), null=True, blank=True, default=date.today)

    p_plan_b =  models.DateField(_("planned planning start"), null=True, blank=False, default=date.today)
    # p_plan_e =  models.DateField(_("planned planning end"), null=True, blank=True)
    p_kickoff = models.DateField(_("planned kick-off date"), null=True, blank=False, default=date.today)
    p_design_b = models.DateField(_("planned design start"), null=True, blank=True)
    p_design_e = models.DateField(_("planned design end"), null=True, blank=True)
    p_dev_b =   models.DateField(_("planned develop start"), null=True, blank=True)
    p_dev_e =   models.DateField(_("planned develop end"), null=True, blank=True)
    p_uat_b =   models.DateField(_("planned UAT start"), null=True, blank=True)
    p_uat_e =   models.DateField(_("planned UAT end"), null=True, blank=True)
    p_launch =  models.DateField(_("planned launch"), null=True, blank=False, default=date.today)
    p_close =   models.DateField(_("planned closing"), null=True, blank=False, default=date.today)

    cbu_req    = models.BooleanField(_("CBU ITSC/EAD/..."), default=False)
    cbu_sow     = models.BooleanField(_("SOW signed"), default=False)
    cbu_po      = models.BooleanField(_("PO received"), default=False)

    a_plan_b = models.DateField(_("actual planning start"), null=True, blank=True)
    # a_plan_e = models.DateField(_("actual planning end"), null=True, blank=True)
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

    req_pro = models.CharField(_("Procurement Review Needed?"), max_length=20, choices=ACTION3, default='00-TBD', blank=True)
    req_sec = models.CharField(_("Info Security Review Needed?"), max_length=20, choices=ACTION3, default='00-TBD', blank=True)
    req_inf = models.CharField(_("Infra Architecure Review Needed?"), max_length=20, choices=ACTION3, default='00-TBD', blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prj_created_by', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prj_updated_by', verbose_name=_('updated by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True,   editable=False)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True,       editable=False)
    last_accessed = models.DateTimeField(blank=True, null=True)
    counts = models.IntegerField(default=1)  # for analytics purpose

    attachment=models.FileField(_("attachment"), upload_to='project/%Y', null=True, blank=True)

    objects = ProjectManager()

    def __str__(self):
        return f'[{self.code}{"*" if self.cf else ""}] {self.title}' 

    @property
    def pyear(self) -> str:
        f'{self.year}{"*" if self.cf else ""}'    

    @property
    def pjcode(self) -> str:
        return f'<new>' if (self.code is None) and (not self.pk is None) else f'{self.code}{"*" if self.cf else ""}'    
    @property
    def CBU_str(self):
        return " ,".join(p.name for p in self.CBUs.all())
    @property
    def strategy_str(self):
        return " ,".join(p.name for p in self.strategy.all())
    @property
    def description_md2(self):
        return md2(self.description) 
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
        send_email = (self.pk is None)          #and (not self.proxy_name == 'ProjectRequest')
        if not send_email and self.CBUs.exists():   #FIXME many-to-many
            old_Project_data = Project.objects.get(pk=self.pk)
            # many-to-many compare FIXME
            if list(old_Project_data.CBUs.all()) != list(self.CBUs.all()):
                send_email = True

        super().save(*args, **kwargs)
        
        # if not c/f, new year is set, then allow to change project code
        if self.code is None or ( self.cf == False and self.code[:2] != f'{self.year % 100}' ):

            next_code = Project.objects.filter(year = self.year).count() + 1

            # self.code = f'{self.year % 100}-{"{:04d}".format(self.pk+2000)}'    #migration upto 1999
            self.code = f'{self.year % 100}-{"{:04d}".format(next_code)}'    
            self.save()

        if send_email:
            # TODO Emails are sent to manager/HOD if the order is new
            # or the CBU has changed
            self.send_new_project_email()
    
    # validation logic
    def clean(self):
        validation_errors = {}

        title = self.title.strip() if self.title else self.title
        # matching_projects = Project.objects.filter(title=title)
        # if self.id:
        #     matching_projects = matching_projects.exclude(pk=self.pk)
        # if matching_projects.exists():
        #     validation_errors['title'] = u"Project name: %s has already exist." % title
        if Project.objects \
                .others(self.pk, title=title, year=self.year) \
                .exclude(state__in=(State.DONE.value, State.CANCEL.value, State.DELETE.value)) \
                .exists():
            validation_errors['title'] = _('Open Project with this title already exists.')

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

        if settings.EMAIL_DEV:
                emails_to.append(settings.EMAIL_TEST_RECEIVER)
        else:
            if settings.PROJECT_SEND_EMAILS_TO_CBUS and self.CBUpm and self.CBUpm.email:
                emails_to.append(self.CBUpm.email)
            if settings.PROJECT_SEND_EMAILS_TO_ASSIGNED and self.pm and self.pm.email:
                emails_to.append(self.pm.email)
                if self.pm.dept.head.email:
                    emails_to.append(self.pm.dept.head.email)
        
        if len(emails_to):
            logger.info("[Project #%s] Sending Project creation email to: %s", self.code, emails_to)
            vals = {
                "id": self.code,
                "PM": str(self.pm) if self.pm else '(Not assigned yet)',
                "CBU": self.CBU_str,
                "CBU_PM": self.CBUpm if self.CBUpm else '(Not assigned yet)',
                "title": self.title,
                "description": self.description or '-',
                "objective": self.objective or '-',
                "url": f'https://psm.{settings.DOMAIN}/project/{self.id}/',
                "sign": settings.SITE_HEADER,
            }

            # if settings.PSM_VIEWER_ENABLED:
            #     email_template = settings.PSM_EMAIL_WITH_URL
            #     vals["url"] = self.get_project_viewer_url()
            # else:
                # email_template = settings.PSM_EMAIL_WITHOUT_URL
            email_template = settings.PSM_EMAIL_WITHOUT_URL
            try:
                send_mail(
                    '[{app}] [#{id}] New Project Created'.format(app=settings.EMAIL_SUBJECT_PREFIX, id=self.code),
                    email_template.format(**vals),
                    settings.APP_EMAIL,
                    emails_to,
                )
            except Exception as e:
                logger.warning("[Project #%s] Error trying to send the Project creation email - %s: %s",
                               self.pk, e.__class__.__name__, str(e))

    def get_project_viewer_url(self):
        """
        Verification token added to the Projects Viewer URL so each one sent through email
        cannot be used to change the order number and access to other orders.
        It uses as input a salt code configured and the ID number.

        See: psmprj/settings_emails.py
        """
        salt = settings.PSM_VIEWER_HASH_SALT
        if not settings.DEBUG and salt == '1two3':
            logger.warning("Insecure salt code used to send email orders, do NOT use it in PRODUCTION")
        # created_at_as_iso = self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # This ISO format is the same used
                                                                                # used by the REST serializer
        token = "{}-{}".format(salt, self.pk)                                   # SHA-1 is enough secure for
        token = sha1(token.encode('utf-8')).hexdigest()                         # this purpose (SHA-2 is too long)
        return settings.PSM_VIEWER_ENDPOINT.format(number=self.number, token=token)

# 
# https://stackoverflow.com/questions/3920909/using-django-how-do-i-construct-a-proxy-object-instance-from-a-superclass-objec
# ----------------------------------------------------------------------------------------------------
# project unplanned request, annual planning : version 10, 11, 12, 20, 21
# ----------------------------------------------------------------------------------------------------
class ProjectRequest(models.Model):
    code = models.CharField(_("Code"), max_length=18, null=True, blank=True) 

    title = models.CharField(_("title"), max_length=200)
    type    = models.CharField(_("type"), max_length=20, choices=PRJTYPE, default=PrjType.ENH.value)
    size    = models.CharField(_("Size"), max_length=20, choices=PRJSIZE, default=PrjSize.SML.value)
    year = models.PositiveIntegerField(_("Year"), default=current_year(), validators=[MinValueValidator(2014), max_value_current_year])
    strategy = models.ManyToManyField(Strategy, blank=True)
    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.PROTECT)
    is_internal = models.BooleanField(_("Internal project"), default=False)
    is_agile = models.BooleanField(_("Agile project"), default=False)
    # is_unplanned = models.BooleanField(_("Unplanned project"), default=False)

    CBUs  = models.ManyToManyField(CBU, blank=True)
    CBUpm = models.ForeignKey(Profile, related_name='req_cbu_pm', verbose_name=_('CBU PM'), on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.SET_NULL)

    released    = models.ForeignKey("Project", related_name='released_prj', on_delete=models.SET_NULL, null=True, blank=True)

    version     = models.CharField(max_length=20, choices=VERSIONS, default=Versions.V10.value )
    asis        = models.TextField(_("As-Is"), max_length=2000, null=True, )
    tobe        = models.TextField(_("To-Be"), max_length=2000, null=True, )
    objective   = models.TextField(_("Objective"), max_length=2000, null=True, )
    consider    = models.TextField(_("Consideration"), max_length=1000, null=True, blank=True)
    quali       = models.TextField(_("Qualitative benefit"), max_length=1000, null=True, blank=True)
    quant       = models.TextField(_("Quantitative benefit"), max_length=1000, null=True, blank=True)
    resource    = models.TextField(_("Resources"), max_length=500, null=True, blank=True)
    img_asis    = models.ImageField(_("As-Is Image"), upload_to='project/%Y', null=True, blank=True)  #default='default.jpg', 
    img_tobe    = models.ImageField(_("To-Be Image"), upload_to='project/%Y', null=True, blank=True)  #default='default.jpg', 

    pm = models.ForeignKey(Profile, related_name='req_pm', verbose_name=_('PM'),
                           on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)
    est_cost = models.DecimalField(_("Est. cost"), decimal_places=0, max_digits=12, blank=True, null=True)

    p_ideation   = models.DateField(_("Planned Ideation start"), null=True, blank=True, default=date.today)
    p_plan_b = models.DateField(_("planned planning start"), null=True, blank=False, default=date.today)
    p_kickoff = models.DateField(_("planned kick-off date"), null=True, blank=False, default=date.today)
    p_design_b = models.DateField(_("planned design start"), null=True, blank=True)
    p_dev_b = models.DateField(_("planned develop start"), null=True, blank=True)
    p_uat_b = models.DateField(_("planned UAT start"), null=True, blank=True)
    p_launch = models.DateField(_("planned launch"), null=True, blank=False, default=date.today)
    p_close = models.DateField(_("planned closing"), null=True, blank=False, default=date.today)

    rel_proj = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prj_req_created_by', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prj_req_updated_by', verbose_name=_('updated by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True,   editable=False)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True,       editable=False)
    counts = models.IntegerField(default=1)  # for analytics purpose

    def __str__(self):
        return self.title if self.pk is None else "[%s] %s" % (self.code, self.title)            

    class Meta:
        permissions = [ ("approve_projectrequest",     "Can approve project plan"),
                        ("access_projectrequest_v20",  "Can access version 20 (BAP approved)"),
                        ("access_projectrequest_v21",  "Can access version 21 (Unplanned approved)"),
                        ("access_projectrequest_cbu",  "Can access by CBU user)"),
                        # ("transfer", "Can transfer project plan to actual project"),
        ]

    objects = ProjectManager()

    @property
    def pjcode(self) -> str:
        prefix = 'BAP-' if self.version == Versions.V20.value else ('UNP-' if self.version == Versions.V21.value else 'REQ-')
        return prefix + f'{self.year % 100}-{"{:04d}".format(self.pk)}'    
        # return self.code if not self.code is None else prefix + f'{self.year % 100}-{"{:04d}".format(self.pk)}'    
    @property
    def CBU_str(self):
        return " ,".join(p.name for p in self.CBUs.all())
    @property
    def strategy_str(self):
        # this is not working... FIXME 
        return " ,".join(p.name for p in self.strategy.all())
    # @property
    # def p_plan_e(self):
    #     return previous_business_day(self.p_design_b, 1)
    @property
    def p_design_e(self):
        return previous_business_day(self.p_dev_b, 1)
    @property
    def p_dev_e(self):
        return previous_business_day(self.p_uat_b, 1)
    @property
    def p_uat_e(self):
        return previous_business_day(self.p_kickoff, 1)

    @property
    def image_tag_asis(self):
        im = get_thumbnail(self.img_asis.file, 'x300', crop='center', quality=99)
        return mark_safe('<img src="%s" width="%s" height="%s" />' % (im.url, im.width, im.height))

    @property
    def image_tag_tobe(self):
        im = get_thumbnail(self.img_tobe.file, 'x300', crop='center', quality=99)
        return mark_safe('<img src="%s" width="%s" height="%s" />' % (im.url, im.width, im.height))

    #override 
    # def check_object_permissions(request, obj) --> View
        # if obj.version == Versions.V20.value and not request.user.has_perm('psm.v-20'):
        #     messages.add_message(request, messages.ERROR, "You do not have access to version 20 (BAP approved') ")
        #     return False
        # if obj.version == Versions.V21.value and not request.user.has_perm('psm.v-21'):
        #     messages.add_message(request, messages.ERROR, "You do not have access to version 21 (Unplanned approved') ")
        #     return False
        # return True    

    def save(self, *args, **kwargs):
        if self.team is None and not self.pm is None:
            self.team = self.pm.team
        if self.dept is None and not self.team is None:
            self.dept = self.team.dept

        super().save(*args, **kwargs)        


    def clean(self):
        validation_errors = {}


        title = self.title.strip() if self.title else self.title
        # matching_projects = ProjectRequest.objects.filter(title=title) # search all version , version=self.version)
        # if self.id:
        #     matching_projects = matching_projects.exclude(pk=self.pk)
        # if matching_projects.exists():
        #     validation_errors['title'] = u"Project name: %s has already exist." % title
        
        if ProjectRequest.objects \
                .others(self.pk, title=title, year=self.year) \
                .exists():
            validation_errors['title'] = _('Project with this title already exists.')

        if len(validation_errors):
            raise ValidationError(validation_errors)

# ----------------------------------------------------------------------------------------------------

# checklist
class ProjectDeliverableType(models.Model):
    name = models.CharField(_("name"), max_length=200, db_index=True)
    desc = models.CharField(_("description"), max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        # app_label = 'common' -> issue in table name...
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
