from django.db import models
from django.conf import settings
from common.codes import *
from django.utils.translation import gettext_lazy as _
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
# https://stackoverflow.com/questions/45309128/circular-dependency-error-in-django
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from users.models import Profile
# from users.models import Profile

# https://github.com/workalendar/workalendar
# https://towardsdatascience.com/the-easiest-way-to-identify-holidays-in-python-58333176af4f
# from workalendar.europe import UnitedKingdom
def year_choices():
    return [(r,r) for r in range(2020, datetime.date.today().year+1)]
def current_year():
    return datetime.date.today().year
def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)  

class CompanyHoliday(models.Model):
    year    = models.IntegerField(default=current_year, validators=[MinValueValidator(2020), max_value_current_year])
    subdiv  = models.CharField(_("Region"), max_length=3, choices=WCAL, default='CA')   # working calendar, exceptional with *
    holiday = models.DateField(blank=False)

    def __str__(self):
        return f'{self.year}-{self.subdiv}-{self.holiday:%Y-%m-%d}'
    class Meta:
        unique_together = ('year', 'subdiv', 'holiday')

class Div(models.Model):
    class Meta:
        verbose_name = _("Division")
        verbose_name_plural = _("Divisions")
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey('users.Profile', related_name='div_head', verbose_name=_('Div head'), on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Dept(models.Model):
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey('users.Profile', related_name='dept_head', verbose_name=_('Dept head'), on_delete=models.SET_NULL, null=True, blank=True)
    div = models.ForeignKey(Div, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    pm_count  = models.SmallIntegerField(_('PM counts'), default=0)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey('users.Profile', related_name='team_head', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dept = models.ForeignKey(Dept, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    pm_count  = models.SmallIntegerField(_('PM counts'), default=0)
#    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_teams")

    class Meta:
        ordering = ("id",)
    def __str__(self):
        return f'{"{:04d}".format(self.pk)}-{self.name}'   # "%s-%s" % (self.pk, self.name)

class GMDM(models.Model):
    class Meta:
        verbose_name = _("GMDM")
        verbose_name_plural = _("GMDM")
    code  = models.CharField(max_length=5, blank=False, null=False)
    name  = models.CharField(max_length=100, blank=False, null=False)
    dept = models.ForeignKey(Dept, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    pm_count  = models.SmallIntegerField(_('PM counts'), default=0)
    def __str__(self):
        return f'[{self.code}] {self.name}'


CBU_TYPE = (
	(0, "Own"),
	(1, "Customer"),
	(2, "Vendor"),
)
class CBU(models.Model):
    """
    CBU: Client business unit, A CBU can be a customer, a provider, a contact, you should
    extend this model to add business logic related with your
    CBU's relationship
    """
    class Meta:
        ordering = ["id"]  # "group", "name"]
        verbose_name = _("CBU")
        verbose_name_plural = _("CBU")

    name = models.CharField(_("name"), max_length=10, db_index=True, unique=True)
    fullname = models.CharField(_("full name"), max_length=100)
    group = models.CharField(_("group name"), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(_("is active"), default=True)
    is_tier1 = models.BooleanField(_("is Tier-1"), default=False)
    cbu_type = models.IntegerField(choices=CBU_TYPE, default=0)
#    phone = models.CharField(_("phone"), max_length=40, null=True, blank=True)
#    mobile = models.CharField(_("mobile"), max_length=40, null=True, blank=True)
#    address = models.CharField(_("address"), max_length=128, null=True, blank=True)
    email = models.EmailField(_("email"), blank=True, null=True)
    website = models.URLField(_("website"), blank=True, null=True)
    comment = models.TextField(_("notes"), max_length=2000, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='CBU_created', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

    def __str__(self):
        return self.name

    # @property
    # def phones(self):
    #     return ", ".join(filter(None, (self.phone, self.mobile)))

class WBS(models.Model):
    class Meta:
        verbose_name = _("WBS")
        verbose_name_plural = _("WBS")

    wbs = models.CharField(_("WBS"), max_length=10, blank=False, null=False, db_index=True)
    name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    cbu = models.CharField(_("CBU"), max_length=20, blank=True, null=True, db_index=True)
    # models.ForeignKey(CBU, on_delete=models.SET_NULL, blank=True, null=True)
    is_sub = models.BooleanField(_("Is sub-project?"), default=False)
    status = models.CharField(max_length=20, blank=True, null=True)
    budget = models.DecimalField(_("Budget"), decimal_places=0, max_digits=12, default=0, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, blank=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

    def __str__(self):
        return f"{self.wbs}{'*' if self.is_sub else ''}" 
