from django.db import models
from django.conf import settings
from common.utils import ROLES
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Org(models.Model):
    name   = models.CharField(max_length=100, blank=True, null=True)
    leader = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    org = models.ForeignKey(Org, on_delete=models.SET_NULL, null=True, blank=True)
#    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_teams")
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
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True)
    org = models.ForeignKey(Org, on_delete=models.SET_NULL, blank=True, null=True)
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