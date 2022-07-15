from django.db import models
from django.conf import settings
from common.codes import *
from django.utils.translation import gettext_lazy as _
from datetime import datetime, date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
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
    cc   = models.CharField(max_length=10, blank=True, null=True)
    head = models.ForeignKey('users.Profile', related_name='div_head', verbose_name=_('Div head'), on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    em_count  = models.SmallIntegerField(_('EM counts'), default=0)
    pm_count  = models.SmallIntegerField(_('PM counts'), default=0)
    notes = models.TextField(_("notes"), max_length=1000, null=True, blank=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)
    def __str__(self):
        return f'{self.name}{ "" if self.is_active else " (inactive)"}'

class Dept(models.Model):
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
    name = models.CharField(max_length=100, blank=False, null=False)
    cc   = models.CharField(max_length=10, blank=True, null=True)
    head = models.ForeignKey('users.Profile', related_name='dept_head', verbose_name=_('Dept head'), on_delete=models.SET_NULL, null=True, blank=True)
    div = models.ForeignKey(Div, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_virtual = models.BooleanField(default=False)
    em_count  = models.SmallIntegerField(_('EM counts'), default=0)
    pm_count  = models.SmallIntegerField(_('PM counts'), default=0)
    notes = models.TextField(_("notes"), max_length=1000, null=True, blank=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)
    def __str__(self):
        return f'{self.name}{"*" if self.is_virtual else ""}{ "" if self.is_active else " (inactive)"}'

class Team(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    cc   = models.CharField(max_length=10, blank=True, null=True)
    head = models.ForeignKey('users.Profile', related_name='team_head', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dept = models.ForeignKey(Dept, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    em_count  = models.SmallIntegerField(_('EM counts'), default=0)
    pm_count  = models.SmallIntegerField(_('PM counts'), default=0)
    notes = models.TextField(_("notes"), max_length=1000, null=True, blank=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)
    def __str__(self):
        return f'{self.name}{ "" if self.is_active else " (inactive)"}'

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
    domain   = models.CharField(_("Domain"), max_length=40, db_index=True, null=True, blank=True)
    # phone = models.CharField(_("phone"), max_length=40, null=True, blank=True)
    # mobile = models.CharField(_("mobile"), max_length=40, null=True, blank=True)
    # address = models.CharField(_("address"), max_length=128, null=True, blank=True)
    # email = models.EmailField(_("email"), blank=True, null=True)
    # website = models.URLField(_("website"), blank=True, null=True)
    comment = models.TextField(_("notes"), max_length=2000, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='CBU_createdby', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

    def __str__(self):
        return f'{self.name}{ "" if self.is_active else " (inactive)"}'

    # @property
    # def phones(self):
    #     return ", ".join(filter(None, (self.phone, self.mobile)))


class GMDM(models.Model):
    # GMDM1 = (
    #     ('A-R&D',               "R&D"),
    #     ('B-Manufacturing',     "Manufacturing"),
    #     ('C-Sales',             "Sales"),
    #     ('D-Administration',    "Administration"),
    #     ('E-ERP',               "ERP"),
    #     ('F-Information Technology',                "Information Technology"),
    #     ('G-Service',             "Service"),
    #     ('Q-Quality',           "Quality"),
    #     ('#N/A',                '#Unknown'),
    # )

    # GMDM2 = (
    #     ('G1000-Product Development       ', 	'Product Development       '),
    #     ('G2000-Production_etc            ', 	'Production_etc            '),
    #     ('G2100-Purchase                  ', 	'Purchase                  '),
    #     ('G2200-MES                       ', 	'MES                       '),
    #     ('G2300-Sales & Operation Planning', 	'Sales & Operation Planning'),
    #     ('G2400-Production Quality        ', 	'Production Quality        '),
    #     ('G3100-Marketing                 ', 	'Marketing                 '),
    #     ('G3200-Sales Support             ', 	'Sales Support             '),
    #     ('G3300-Sales_etc                 ', 	'Sales_etc                 '),
    #     ('G4100-HR                        ', 	'HR                        '),
    #     ('G4200-Finance                   ', 	'Finance                   '),
    #     ('G4210-Cost                      ', 	'Cost                      '),
    #     ('G4300-Advertisement             ', 	'Advertisement             '),
    #     ('G4400-Planning/Legal            ', 	'Planning/Legal            '),
    #     ('G4500-General Affairs           ', 	'General Affairs           '),
    #     ('G4900-Admin_etc                 ', 	'Admin_etc                 '),
    #     ('G5000-ERP                       ', 	'ERP                       '),
    #     ('G5100-Sales ERP                 ', 	'Sales ERP                 '),
    #     ('G6000-Business Intelligence     ', 	'Business Intelligence     '),
    #     ('G6100-Information Technology    ', 	'Information Technology    '),
    #     ('G6200-IT Infrastructure         ', 	'IT Infrastructure         '),
    #     ('G6300-Security                  ', 	'Security                  '),
    #     ('G6400-Consulting/Services/Others', 	'Consulting/Services/Others'),
    #     ('G6500-Big Data                  ', 	'Big Data                  '),
    #     ('G7000-CRM                       ', 	'CRM                       '),
    #     ('G7100-Maintenance Technique     ', 	'Maintenance Technique     '),
    #     ('G7200-Oversea Service           ', 	'Oversea Service           '),
    #     ('G7250-Domestic Service          ', 	'Domestic Service          '),
    #     ('G7300-TMS                       ', 	'TMS                       '),
    #     ('G8000-Quality Management        ', 	'Quality Management        '),
    #     ('#N/A', 	                            '#Unknown'),
    # )
    GMDM1 = (
        ('R&D',               "R&D"),
        ('Manufacturing',     "Manufacturing"),
        ('Sales',             "Sales"),
        ('Administration',    "Administration"),
        ('ERP',               "ERP"),
        ('IT',                "IT"),
        ('Service',           "Service"),
        ('Quality',           "Quality"),
        ('#N/A',              '#Unknown'),
    )
    GMDM2 = (
        ('Product Development       ', 	'Product Development       '),
        ('Production_etc            ', 	'Production_etc            '),
        ('Purchase                  ', 	'Purchase                  '),
        ('MES                       ', 	'MES                       '),
        ('Sales & Operation Planning', 	'Sales & Operation Planning'),
        ('Production Quality        ', 	'Production Quality        '),
        ('Marketing                 ', 	'Marketing                 '),
        ('Sales Support             ', 	'Sales Support             '),
        ('Sales_etc                 ', 	'Sales_etc                 '),
        ('HR                        ', 	'HR                        '),
        ('Finance                   ', 	'Finance                   '),
        ('Cost                      ', 	'Cost                      '),
        ('Advertisement             ', 	'Advertisement             '),
        ('Planning/Legal            ', 	'Planning/Legal            '),
        ('General Affairs           ', 	'General Affairs           '),
        ('Admin_etc                 ', 	'Admin_etc                 '),
        ('ERP                       ', 	'ERP                       '),
        ('Sales ERP                 ', 	'Sales ERP                 '),
        ('Business Intelligence     ', 	'Business Intelligence     '),
        ('Information Technology    ', 	'Information Technology    '),
        ('IT Infrastructure         ', 	'IT Infrastructure         '),
        ('Security                  ', 	'Security                  '),
        ('Consulting/Services/Others', 	'Consulting/Services/Others'),
        ('Big Data                  ', 	'Big Data                  '),
        ('CRM                       ', 	'CRM                       '),
        ('Maintenance Technique     ', 	'Maintenance Technique     '),
        ('Oversea Service           ', 	'Oversea Service           '),
        ('Domestic Service          ', 	'Domestic Service          '),
        ('TMS                       ', 	'TMS                       '),
        ('Quality Management        ', 	'Quality Management        '),
        ('#N/A', 	                    '#Unknown'),
    )

    USERTYPE = (
        ('Corporate user',        "Corporate user"),
        ('Dealer',                "Dealer"),
        ('Corporate+Dealer',      "Corporate + Dealer user"),
        ('Customer',              "Customer"),
        ('Public',                "Public"),
    )

    APPTYPE = (
        ('Package',      "Package"),
        ('Package+Dev',  "Package+Dev"),
        ('SaaS',         "SaaS"),
        ('SasS+Dev',     "SaaS+Dev"),
        ('PaaS+Dev',     "PaaS+Dev"),
        ('Custom App',   "Custom App"),
        ('Mobile App',   "Mobile App"),
        ('External App', "External App"),
        ('Desktop S/W',  "Desktop S/W"),
    )

    CRITICAL = (
        ('1-Very High',   "Very high"),
        ('2-High',        "High"),
        ('3-Medium',      "Medium"),
        ('4-Low',         "Low"),
        ('9-TBD',         "TBD"),
    )

    NO_USER = (
        ('< 100',    "< 100"),
        ('< 250',    "< 250"),
        ('< 500',    "< 500"),
        ('< 1500',   "< 1500"),
        ('< 5000',   "< 5000"),
        ('< 10000',  "< 10000"),
        ('< 50000',  "< 50000"),
        ('> 50000',  "> 50000"),
    )

    NO_CUSTOM = (
        ('< 10',   "< 10"),
        ('< 50',   "< 50"),
        ('< 100',  "< 100"),
        ('< 250',  "< 250"),
        ('< 500',  "< 500"),
        ('< 750',  "< 750"),
        ('< 1000', "< 1000"),
        ('< 2000', "> 1000"),
        ('> 2000', "> 2000"),
    )

    class Meta:
        verbose_name = _("GMDM")
        verbose_name_plural = _("GMDM")

        permissions = [ ("admin_gmdm",     "Can admin GMDM)"),
        ]


    code  = models.CharField(max_length=10, blank=False, null=False)
    name  = models.CharField(max_length=100, blank=False, null=False)

    outline = models.TextField(_("Description"), max_length=1000, blank=True, null=True)
    platform = models.CharField(_("Platform"), max_length=150, blank=True, null=True)
    os    = models.CharField(_("OS"), max_length=100, blank=True, null=True)
    db    = models.CharField(_("DB"), max_length=100, blank=True, null=True)
    lang  = models.CharField(_("Languages"), max_length=100, blank=True, null=True)
    ui    = models.CharField(_("UI/URL"), max_length=150, blank=True, null=True)
    no_screen = models.CharField(_("no of screens"),    max_length=20, choices=NO_CUSTOM, blank=True, null=True)
    no_if     = models.CharField(_("no of interface"),  max_length=20, choices=NO_CUSTOM, blank=True, null=True)
    no_table  = models.CharField(_("no of tables"),     max_length=20, choices=NO_CUSTOM, blank=True, null=True)

    usertype = models.CharField(_("User type"), max_length=100, choices=USERTYPE, blank=True, null=True)
    no_user = models.CharField(_("no of users"), max_length=20, choices=NO_USER, blank=True, null=True)
    apptype = models.CharField(_("App type"), max_length=100, choices=APPTYPE, blank=True, null=True)
    operator = models.CharField(_("Operator"), max_length=100, blank=True, null=True)

    initial = models.DateField(_("Initial launching"), null=True, blank=True)
    latest  = models.DateField(_("Lasted upgrade"), null=True, blank=True )
    decommission  = models.DateField(_("Decommision"), null=True, blank=True )

    dept = models.ForeignKey('common.Dept', on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey('common.Team', on_delete=models.SET_NULL, null=True, blank=True)
    # owner1 = models.ForeignKey('users.Profile', related_name='app_primary',   on_delete=models.SET_NULL, null=True, blank=True)
    sme = models.CharField(_("SME"), max_length=100, blank=True, null=True)
    assignment = models.CharField(_("Assignment Group"), max_length=100, blank=True, null=True)
    assignee = models.CharField(_("Assignee"), max_length=100, blank=True, null=True)

    critical = models.CharField(_("Criticality"), max_length=50, choices=CRITICAL, default='4-Low', null=True)
    dr = models.BooleanField(_("DR ready"), default=False)
    level1 = models.CharField(_("Level 1"), max_length=50, choices=GMDM1, blank=True, null=True)
    level2 = models.CharField(_("Level 2"), max_length=50, choices=GMDM2, blank=True, null=True)
    CBU = models.ForeignKey('common.CBU', null=True, on_delete=models.SET_NULL)
    CBUteam  = models.CharField(_("CBU team"), max_length=100, blank=True, null=True)

    grouping = models.CharField(_("Grouping"), max_length=100, blank=True, null=True)
    remark = models.CharField(_("Remark"), max_length=400, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='GMDM_createdby', verbose_name=_('created by'),
                                   on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='GMDM_updated', verbose_name=_('updated by'),
                                   on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(_("created at"), auto_now_add=True, editable=False, null=True, blank=True)  #auto_now_add=True,
    updated_on = models.DateField(_("updated_on"), auto_now=True, editable=False, null=True, blank=True)  #auto_now=True,     , default=timezone.now()

    pm_count  = models.SmallIntegerField(_('PM counts'), default=0, blank=True, null=True)
    def __str__(self):
        return f'[{self.code}] {self.name} { "(inactive)" if self.decommission else ""}'

