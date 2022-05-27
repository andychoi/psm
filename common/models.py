from django.db import models
from django.conf import settings
from common.utils import ROLES
from django.utils.translation import gettext_lazy as _
import enum

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
# from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
STATES = (
    (State.BACKLOG.value, _('Backlog')),
    (State.TO_DO.value, _('To Do')),
    (State.DOING.value, _('Doing')),
    (State.HOLD.value, _('Blocked')),
    (State.DONE.value, _('Done')),
    (State.CANCEL.value, _('Canceled'))
)

class Priority(enum.Enum):
    """
    The priority of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    LOW = '00-low'
    NORMAL = '10-normal'
    HIGH = '20-high'
    CRITICAL = '30-critical'

PRIORITIES = (
    (Priority.LOW.value, _('Low')),
    (Priority.NORMAL.value, _('Normal')),
    (Priority.HIGH.value, _('High')),
    (Priority.CRITICAL.value, _('Critical')),
)


class Status(enum.Enum):
    NA = '00-notApplicable'
    GREEN = '10-green'
    YELLOW = '20-yellow'
    RED = '30-red'
    COMPLETED = '90-completed'

STATUS = (
    (Status.GREEN.value, _('Green')),
    (Status.YELLOW.value, _('Yellow')),
    (Status.RED.value, _('Red')),
    (Status.COMPLETED.value, _('Completed')),
    (Status.NA.value, _('N/A')),
)

class Phase(enum.Enum):
    PRE_PLAN = '0-Pre-Planning'
    PLANNING = '1-Planning'
    DESIGN = '2-Design'
    DEVELOP = '3-Develop'
    TESTING = '4-Testing'
    LAUNCH = '5-Launch'
    COMPLETED = '8-Completed'
    CLOSED = '9-Closed'

PHASE = (
    ('0-Pre-Planning',"Pre-Planning"),
    ('1-Planning',"Planning"),
    ('2-Planning',"Design"),
    ('3-Planning',"Development"),
    ('4-Testing',"Testing"),        
    ('5-Launch',"Launch"),        
    ('6-Completed',"Completed"),        
    ('9-Closed',"Closed")        
)

class PrjType(enum.Enum):
    """
    The priority of the Project
    (codes are prefixed with numbers to be easily sorted in the DB).
    """
    MAJOR = '00-Major'
    SMALL = '10-Small'
    ENH = '20-Enhancement'
    UNC = '90-Unclassifed'

PRJTYPE = (
    (PrjType.MAJOR.value, _('Major')),
    (PrjType.SMALL.value, _('Small')),
    (PrjType.ENH.value, _('Enhancement')),
    (PrjType.UNC.value, _('Unclassified')),
)

class State3(enum.Enum):
    TBD = '0-TBD'
    YES = '1-Yes'
    NO  = '2-No'
STATE3 = (
    (State3.TBD.value, _('TBD')),
    (State3.YES.value, _('Yes')),
    (State3.NO.value, _('No')),
)

class ReviewTypes(enum.Enum):
    PRO = '00-Procurement'
    SEC = '10-Security'
    INF = '20-Infra-Architecture'
    APP = '30-App-Architecture'
    MGT = '90-Management'
REVIEWTYPES = (
    (ReviewTypes.PRO.value, _('00-Procurement')),
    (ReviewTypes.SEC.value, _('10-Security')),
    (ReviewTypes.INF.value, _('20-Infra-Architecture')),
    (ReviewTypes.APP.value, _('30-App-Architecture')),
    (ReviewTypes.MGT.value, _('90-Management'))
)



PUBLISH = (
	(0,"Draft"),
	(1,"Publish"),
	(2, "Delete")
)


# Create your models here.

class Div(models.Model):
    class Meta:
        verbose_name = _("Division")
        verbose_name_plural = _("Divisions")
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey('ExtendUser', verbose_name=_('Div head'), on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Dept(models.Model):
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey('ExtendUser', verbose_name=_('Dept head'), on_delete=models.SET_NULL, null=True, blank=True)
    div = models.ForeignKey(Div, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey('ExtendUser', verbose_name=_('Team head'), on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    dept = models.ForeignKey(Dept, on_delete=models.SET_NULL, null=True, blank=True)
    div = models.ForeignKey(Div, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
#    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_teams")
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="team_created", null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    # def get_users(self):
    #     return ",".join(
    #         [str(_id) for _id in list(self.users.values_list("id", flat=True))]
    #     )
        # return ','.join(list(self.users.values_list('id', flat=True)))

from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.deletion import CASCADE

class ExtendUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, verbose_name=_('external user'), null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=200, blank=True, null=True)
    manager = models.OneToOneField(User,on_delete=models.CASCADE, related_name='manager', verbose_name=_('manager'), null=True, blank=True)
    u_team = models.ForeignKey('Team', verbose_name=_('Team'), on_delete=models.SET_NULL, blank=True, null=True)
    u_dept = models.ForeignKey('Dept', verbose_name=_('Dept'), on_delete=models.SET_NULL, blank=True, null=True)
    u_div = models.ForeignKey('Div', verbose_name=_('Div'), on_delete=models.SET_NULL, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLES, default="USER")
    is_external = models.BooleanField(_("External user?"), default=False)
    is_active = models.BooleanField(default=True)
    is_organization_admin = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ext_user_created", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, blank=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    def __str__(self):
        # FIXME
        return getattr(self.user, 'username', self.name)
        #return self.name

    @property
    def is_admin(self):
        return self.is_organization_admin



class CBU(models.Model):
    """
    CBU: Client business unit, A CBU can be a customer, a provider, a contact, you should
    extend this model to add business logic related with your
    CBU's relationship
    """
    class Meta:
        ordering = ["name"]
        verbose_name = _("CBU")
        verbose_name_plural = _("CBUs")

    name = models.CharField(_("name"), max_length=10, db_index=True, unique=True)
    fullname = models.CharField(_("full name"), max_length=100)
    group = models.CharField(_("group name"), max_length=100, blank=True, null=True)
    email = models.EmailField(_("email"), blank=True, null=True)
    website = models.URLField(_("website"), blank=True, null=True)
    is_tier1 = models.BooleanField(_("is Tier-1"), default=False)
    is_company = models.BooleanField(_("is company"), default=True)
#    phone = models.CharField(_("phone"), max_length=40, null=True, blank=True)
#    mobile = models.CharField(_("mobile"), max_length=40, null=True, blank=True)
#    address = models.CharField(_("address"), max_length=128, null=True, blank=True)
    comment = models.TextField(_("notes"), max_length=2000, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='CBU_created', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    def __str__(self):
        return self.name

    # @property
    # def phones(self):
    #     return ", ".join(filter(None, (self.phone, self.mobile)))
