from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.


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

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='WBS_createdby', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False, blank=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

    def __str__(self):
        return f"{self.wbs}{'*' if self.is_sub else ''} - {self.name}" 

class Employee(models.Model):
    emp_id = models.CharField(_("EmpID"), max_length=10, blank=False, null=False, db_index=True)
    emp_name = models.CharField(max_length=50, blank=True, null=True)
    dept_code = models.CharField(max_length=10, blank=True, null=True)
    dept_name = models.CharField(max_length=50, blank=True, null=True)
    l = models.PositiveSmallIntegerField(blank=True, null=True)
    cc = models.CharField(max_length=10, blank=True, null=True)
    job = models.CharField(max_length=50, blank=True, null=True)
    manager_id = models.CharField(_("ManagerID"), max_length=10, blank=False, null=False, db_index=True)
    email = models.CharField(_("Email"), max_length=50, blank=False, null=False, db_index=True)
    create_date = models.DateTimeField(_("Create_date"), blank=True, null=True)
    terminated = models.DateTimeField(_("Terminated"), blank=True, null=True)
    updated_on = models.DateTimeField(_("updated_on"), auto_now=True, editable=False)

    def __str__(self):
        return f"{self.emp_id} { '(terminated)' if self.terminated else ''}" 
