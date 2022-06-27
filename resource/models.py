import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from common.codes import PUBLISH
from users.models import Profile
from datetime import date
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from common.dates import workdays_us
from common.codes import SKILLLEVEL, SkillLevel

# Create your models here.
# https://mattsch.com/2021/05/28/django-django_tables2-and-bootstrap-table/
# Refer: https://christosstath10.medium.com/create-your-own-point-of-sale-c25f8b1ff93b

def year_choices():
    return [(r,r) for r in range(2020, datetime.date.today().year+1)]
def current_year():
    return datetime.date.today().year
def min_year():
    return datetime.date.today().year - 4
def max_value_current_year(value):
    return MaxValueValidator(current_year()+1)(value)


class Skill(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    level = models.CharField(_("Skill level"), max_length=20, choices=SKILLLEVEL, default = SkillLevel.MID.value )
    group = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(_("Description"), max_length=2000, null=True, )
    is_active = models.BooleanField(default=True)

    # auto_now_add=True
    created_at = models.DateField(_("created at"), default=date.today, editable=False)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    counts  = models.SmallIntegerField(_('Skill counts'), default=0)

    def __str__(self):
        return f"{self.name}{'*' if not self.is_active else ''}"


class ResourceManager(models.Manager):
    def active(self):
        return self.filter(active=True)

"""
    working days per staff's work schedule
"""
class Resource(models.Model):
    MAX_MM      = 150    # 150%
    MAX_DAYS    = 31    # 150%
    
    # category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    staff = models.ForeignKey(Profile, related_name='staff', on_delete=models.PROTECT, null=True, blank=False)
    year = models.PositiveSmallIntegerField(default=date.today().year)
    skills = models.ManyToManyField(Skill, blank=True)

    # working days
    m01 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=1))
    m02 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(29)], default=workdays_us(m=2))
    m03 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=3))
    m04 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(30)], default=workdays_us(m=4))
    m05 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=5))
    m06 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(30)], default=workdays_us(m=6))
    m07 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=7))
    m08 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=8))
    m09 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(30)], default=workdays_us(m=9))
    m10 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=10))
    m11 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(30)], default=workdays_us(m=11))
    m12 = models.IntegerField( validators = [MinValueValidator(0), MaxValueValidator(31)], default=workdays_us(m=12))

    active     = models.BooleanField(default=True)
    created_at = models.DateField(_("created at"), default=date.today, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="res_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="res_updated_by", null=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    broswer = ResourceManager()

    def __str__(self):
        return f'{self.staff} ({self.year})' 
    
    class Meta:
        verbose_name_plural = 'Resources'
        unique_together = ['staff', 'year']

    def skill_names(self):
        return " ,".join(p.name for p in self.skills.all())

    def save(self, *args, **kwargs):
        # self.final_value = self.discount_value if self.discount_value > 0 else self.value
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.year}] {self.staff}'

    def man_hours(self):
        return f'{self.m01 * 168 / 100} hr'


    # def get_edit_url(self):
    #     return reverse('update_resourceplan', kwargs={'pk': self.id})

    # def get_delete_url(self):
    #     return reverse('delete_resourceplan', kwargs={'pk': self.id})


class ProjectPlan(models.Model):
    project = models.ForeignKey('psm.Project', related_name='project_plan', on_delete=models.PROTECT, null=True, blank=False)
    year = models.PositiveIntegerField(_("Year"), default=current_year())
    status = models.IntegerField(choices=PUBLISH, default=1) 

    # auto_now_add=True
    created_at = models.DateField(_("created at"), default=date.today, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="pp_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="pp_updated_by", null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ['project', 'year']
    def __str__(self):
        return f'{self.project} ({self.year})' 

class ResourcePlan(models.Model):
    staff = models.ForeignKey(Profile, related_name='staf_plan', on_delete=models.PROTECT, null=True, blank=False)
    year = models.PositiveIntegerField(_("Year"), default=current_year())
    status = models.IntegerField(choices=PUBLISH, default=1) 

    # auto_now_add=True
    created_at = models.DateField(_("created at"), default=date.today, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rp_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rp_updated_by", null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ['staff', 'year']

    def __str__(self):
        return f'{self.staff} ({self.year})' 

"""
    resource based planning by staff
    project based planning by PM
    reconcile by manager/HOD
"""
class RPPlanItem(models.Model):
    class Meta:
        verbose_name = _("Time Allocation")
        verbose_name_plural = _("Time Allocations")
        unique_together = [['year', 'staff', 'project']]

    pr = models.ForeignKey(ResourcePlan, on_delete=models.CASCADE, null=True, blank=True)
    pp = models.ForeignKey(ProjectPlan, on_delete=models.CASCADE, null=True, blank=True)

    year = models.PositiveIntegerField(_("Year"), default=current_year())
    staff = models.ForeignKey(Profile, related_name='staf_planitem', on_delete=models.SET_NULL, blank=True, null=True )
    project = models.ForeignKey('psm.Project', related_name='project_planitem', on_delete=models.PROTECT, null=True, blank=True)
    
    m01 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m02 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m03 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m04 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m05 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m06 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m07 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m08 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m09 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m10 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m11 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m12 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m13 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m14 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])
    m15 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(Resource.MAX_MM)])

    # auto_now_add=True
    created_at = models.DateField(_("created at"), default=date.today, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="pitem_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="pitem_updated_by", null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # self.final_value = self.discount_value if self.discount_value > 0 else self.value
        if not self.year:
            if self.pr:
                self.year = ResourcePlan.objects.get(pk=self.pr.pk).year
            # self.save()
            if self.pp:
                self.year = ProjectPlan.objects.get(pk=self.pp.pk).year
            # self.save()

        super().save(*args, **kwargs)

    @property
    def r_no(self):
        return '' if not self.pr else self.pr.id
    @property
    def r_staff(self):
        return '' if not self.pr else self.pr.staff
    @property
    def p_no(self):
        return '' if not self.pp else self.pp.id
    @property
    def p_proj(self):
        return '' if not self.pp else self.pp.project

    def __str__(self):
        if self.pr:
            return f'{self.pr.staff} ({self.year})' 
        # self.save()
        if self.pp:
            return f'{self.pp.project} ({self.year})' 

    # reference: https://stackoverflow.com/questions/867120/how-to-check-value-transition-in-django-django-admin

    # @receiver(post_delete, sender=RPPlanItem)
    # def delete_order_item(sender, instance, **kwargs):
    #     product = instance.product
    #     product.qty += instance.qty
    #     product.save()
    #     instance.order.save()
        # validation logic
