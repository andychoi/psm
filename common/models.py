from django.db import models
from django.conf import settings
from common.utils import ROLES
from django.utils.translation import gettext_lazy as _

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
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=200, blank=True, null=True)
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

    name = models.CharField(_("name"), max_length=10, db_index=True)
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
