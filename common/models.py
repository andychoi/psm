from django.db import models
from django.conf import settings
from common.utils import *
from django.utils.translation import gettext_lazy as _

# https://stackoverflow.com/questions/45309128/circular-dependency-error-in-django
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from users.models import Profile
from users.models import Profile

class Div(models.Model):
    class Meta:
        verbose_name = _("Division")
        verbose_name_plural = _("Divisions")
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey(Profile, related_name='div_head', verbose_name=_('Div head'), on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Dept(models.Model):
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey(Profile, related_name='dept_head', verbose_name=_('Dept head'), on_delete=models.SET_NULL, null=True, blank=True)
    div = models.ForeignKey(Div, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    head = models.ForeignKey(Profile, related_name='team_head', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dept = models.ForeignKey(Dept, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
#    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_teams")

    class Meta:
        ordering = ("name",)
    def __str__(self):
        return self.name

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
    email = models.EmailField(_("email"), blank=True, null=True)
    website = models.URLField(_("website"), blank=True, null=True)
    is_active = models.BooleanField(_("is active"), default=True)
    is_tier1 = models.BooleanField(_("is Tier-1"), default=False)
#    phone = models.CharField(_("phone"), max_length=40, null=True, blank=True)
#    mobile = models.CharField(_("mobile"), max_length=40, null=True, blank=True)
#    address = models.CharField(_("address"), max_length=128, null=True, blank=True)
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
    status = models.CharField(max_length=20, blank=True, null=True)
    budget = models.DecimalField(_("Budget"), decimal_places=0, max_digits=12, default=0, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, blank=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

    def __str__(self):
        return self.wbs
