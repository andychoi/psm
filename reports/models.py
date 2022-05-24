# importing django models and users
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from django.utils.html import mark_safe
# from ckeditor.fields import RichTextField

from CBU.models import CBU
from psm.models import Status

PUBLISH = (
	(0,"Draft"),
	(1,"Publish"),
	(2, "Delete")
)
STATUS = (
    (Status.GREEN.value, _('Green')),
    (Status.YELLOW.value, _('Yellow')),
    (Status.RED.value, _('Red')),
    (Status.COMPLETED.value, _('Completed')),
    (Status.NA.value, _('N/A')),
)
# creating an django model class
class Report(models.Model):

    project = models.ForeignKey('psm.Project', on_delete=models.CASCADE, blank=True, null=True)
    # title field using charfield constraint with unique constraint
    title = models.CharField(max_length=200)
    CBU = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)

    status_o = models.CharField(_("status overall"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_t = models.CharField(_("-schedule"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_b = models.CharField(_("-budget"), max_length=20, choices=STATUS, default=Status.GREEN.value)
    status_s = models.CharField(_("-scope"), max_length=20, choices=STATUS, default=Status.GREEN.value)

	# content field to store our post
    content_a = models.TextField(_("Acomplishment"))
    content_p = models.TextField(_("Plan for next period"))
    # content_p = RichTextField()
    issue = models.TextField(_("Issues & Plan"))

	# status of post
    status = models.IntegerField(choices=PUBLISH, default=0)

    created_on = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
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

    Report = models.ForeignKey(Report, on_delete=models.CASCADE)
    no = models.SmallIntegerField(_("No"), blank=True, default=0)
    stage = models.CharField(_("stage"), max_length=200, blank=True)
    description = models.CharField(_("description"), max_length=200, blank=True)
    start = models.DateField(blank=True, null=True)
    finish = models.DateField(blank=True, null=True)
    complete = models.IntegerField(_("complete%"), default=0)
    status = models.CharField(_("status overall"), max_length=20, choices=STATUS, default=Status.NA.value)

    def __str__(self):
        return self.stage + self.description