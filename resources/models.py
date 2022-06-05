import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from common.utils import PUBLISH
from users.models import Profile
from datetime import date

# Create your models here.

def year_choices():
    return [(r,r) for r in range(2020, datetime.date.today().year+1)]
def current_year():
    return datetime.date.today().year
def min_year():
    return datetime.date.today().year - 4
def max_value_current_year(value):
    return MaxValueValidator(current_year()+1)(value)

class ResourcePlan(models.Model):
    # staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Profile, related_name='staff', on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveIntegerField(_("Year"), default=current_year())
    status = models.IntegerField(choices=PUBLISH, default=0) 

    # auto_now_add=True
    created_on = models.DateField(_("created at"), default=date.today, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rp_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rp_updated_by", null=True, on_delete=models.SET_NULL)

class ResourcePlanItem(models.Model):
    class Meta:
        verbose_name = _("Time Allocation")
        verbose_name_plural = _("Time Allocations")

    rp = models.ForeignKey(ResourcePlan, on_delete=models.CASCADE)
    project = models.ForeignKey('psm.Project', on_delete=models.CASCADE, blank=True, null=True)
    w01 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w02 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w03 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w04 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w05 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w06 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w07 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w08 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w09 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    w10 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
