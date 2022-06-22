import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from common.utils import PUBLISH
from users.models import Profile
from datetime import date

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

class ResourceManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class Resource(models.Model):
    MAX_MM = 150    # 150%
    
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=150, unique=True)
    # category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    year = models.PositiveSmallIntegerField(default=date.today().year)

#JSON field?
# 
    m01 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m02 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m03 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m04 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m05 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m06 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m07 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m08 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m09 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m10 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m11 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])
    m12 = models.IntegerField(default = 100, validators = [MinValueValidator(0), MaxValueValidator(MAX_MM)])


    objects = models.Manager()
    broswer = ResourceManager()

    class Meta:
        verbose_name_plural = 'Resources'

    def save(self, *args, **kwargs):
        self.final_value = self.discount_value if self.discount_value > 0 else self.value
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def man_hours(self):
        return f'{self.m01 * 168 / 100} hr'

    def get_edit_url(self):
        return reverse('update_resourceplan', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('delete_resourceplan', kwargs={'pk': self.id})


class ResourcePlan(models.Model):
    # staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Profile, related_name='staff', on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveIntegerField(_("Year"), default=current_year())
    status = models.IntegerField(choices=PUBLISH, default=0) 

    # auto_now_add=True
    created_at = models.DateField(_("created at"), default=date.today, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rp_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rp_updated_by", null=True, on_delete=models.SET_NULL)

class ResourcePlanItem(models.Model):
    class Meta:
        verbose_name = _("Time Allocation")
        verbose_name_plural = _("Time Allocations")

    rp = models.ForeignKey(ResourcePlan, on_delete=models.CASCADE)
    project = models.ForeignKey('psm.Project', on_delete=models.SET_NULL, blank=True, null=True)
    m01 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m02 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m03 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m04 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m05 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m06 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m07 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m08 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m09 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m10 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m11 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])
    m12 = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(100)])

    @receiver(post_delete, sender=OrderItem)
    def delete_order_item(sender, instance, **kwargs):
        product = instance.product
        product.qty += instance.qty
        product.save()
        instance.order.save()
