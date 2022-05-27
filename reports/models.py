# importing django models and users
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from django.utils.html import mark_safe
from datetime import datetime   
# from ckeditor.fields import RichTextField

from common.models import CBU, Dept, Div, PUBLISH, STATUS
from psm.models import Status


class ReportDist(models.Model):
    project = models.ForeignKey('psm.Project', on_delete=models.CASCADE, blank=True, null=True)
    # title field using charfield constraint with unique constraint
    is_active = models.BooleanField(_("Is Active?"), default=True)
    recipients_to = models.TextField(_("Recipients (to)"), max_length=1000, blank=True, null=True)
    recipients_cc = models.TextField(_("Recipients (cc)"), max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = _("Report Distribution List")
        verbose_name_plural = _("Report Distribution List")    


# creating an django model class
class Report(models.Model):

    project = models.ForeignKey('psm.Project', on_delete=models.CASCADE, blank=True, null=True)
    # title field using charfield constraint with unique constraint
    title = models.CharField(max_length=200)
    CBU = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.PROTECT)
    div = models.ForeignKey(Div, blank=True, null=True, on_delete=models.PROTECT)

    status_o = models.CharField(_("Overall"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_t = models.CharField(_("Schedule"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_b = models.CharField(_("Budget"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_s = models.CharField(_("Scope"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    # status_o = models.IntegerField(_("Overall"), choices=STATUS, default=0)
    # status_t = models.IntegerField(_("Schedule"), choices=STATUS, default=0)
    # status_b = models.IntegerField(_("Budget"), choices=STATUS, default=0)
    # status_s = models.IntegerField(_("Scope"), choices=STATUS, default=0)

	# content field to store our post
    content_a = models.TextField(_("Acomplishment"))
    content_p = models.TextField(_("Plan for next period"))
    # content_p = RichTextField()
    issue = models.TextField(_("Issues & Plan"))

	# status of post
    status = models.IntegerField(choices=PUBLISH, default=0)
    progress = models.SmallIntegerField(_("complete%"), default=0)
    is_monthly = models.BooleanField(_("Is Monthly?"), default=False)

    created_on = models.DateField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="report_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="report_updated_by", null=True, on_delete=models.SET_NULL)


	# meta for the class
    class Meta:
        ordering = ['-updated_on']
	# used while managing models from terminal
    def __str__(self):
        return self.title


class Milestone(models.Model):
    class Meta:
        verbose_name = _("Milestone")
        verbose_name_plural = _("Milestones")

    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    no = models.SmallIntegerField(_("No"), blank=True, default=0)  #for sorting purpose
    stage = models.CharField(_("stage"), max_length=50, blank=True)
    description = models.CharField(_("description"), max_length=100, blank=True)
    start = models.DateField(blank=True, null=True)
    finish = models.DateField(blank=True, null=True)
    progress = models.IntegerField(_("complete%"), default=0)
    status = models.CharField(_("status overall"), max_length=20, choices=STATUS, default=Status.NA.value)
    # status = models.IntegerField(_("Task Status"), choices=STATUS, default=0)

    def __str__(self):
        # return self.stage + ' - ' + self.description
        return self.description

# creating an django model class
class ReportRisk(models.Model):

    project = models.ForeignKey('psm.Project', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    owner = models.CharField(max_length=200, null=True, blank=True)
    CBU = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.PROTECT)
    div = models.ForeignKey(Div, blank=True, null=True, on_delete=models.PROTECT)

	# content field to store our post
    risk = models.TextField(_("Risk Details"))
    plan = models.TextField(_("Mitigation Plan"))

    status = models.IntegerField(choices=PUBLISH, default=0)
    report_on = models.DateField(_("Reporting On"), default=datetime.now, blank=False)
    created_on = models.DateField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="riskr_eport_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="risk_report_updated_by", null=True, on_delete=models.SET_NULL)

	# meta for the class
    class Meta:
        ordering = ['-updated_on']
        verbose_name = _("Risk Report")
        verbose_name_plural = _("Risk Reports")        
    def __str__(self):
        return self.project.title


