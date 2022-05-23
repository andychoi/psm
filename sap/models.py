from django.db import models
from django.conf import settings
from common.utils import ROLES
from django.utils.translation import gettext_lazy as _

# Create your models here.

# from django.db import models
# from django.contrib.auth.models import User
# from django.db.models.base import Model
# from django.db.models.deletion import CASCADE

class WBS(models.Model):
    class Meta:
        verbose_name = _("WBS")
        verbose_name_plural = _("WBS")

    wbs = models.CharField(_("WBS"), max_length=10, blank=False, null=False, db_index=True)
    name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    cbu = models.CharField(_("CBU"), max_length=20, blank=True, null=True, db_index=True)
    # models.ForeignKey(CBU, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    budget = models.DecimalField(_("Budget"), decimal_places=0, max_digits=12, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, blank=True)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True, editable=False)

    def __str__(self):
        return self.wbs
