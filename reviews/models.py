from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date

from common.models import CBU, Dept, Div
from common.utils import STATE3, STATUS, Status, PRIORITIES, Priority, REQTYPES, ReqTypes, DECISIONS, Decision
from psm.models import Project

# Create your models here.
# https://stackoverflow.com/questions/241250/single-table-inheritance-in-django

# creating an django model class
class Review(models.Model):

    reqtype = models.CharField(_("Review Type"), max_length=40, choices=REQTYPES, default=ReqTypes.PRO.value)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=200)

    # related = models.ManyToManyField( to='common.Dept', related_name='related_depts')
    state = models.CharField(_("PM Requested?"), max_length=10, choices=STATE3, null=True, blank=True)
    req_content = models.TextField(_("Review request"), null=True, blank=True)
    proc_start = models.DateField(_("DESIRED start date"), null=True, blank=True)
    onboaddt = models.DateField(_("DESIRED onboarding date"), null=True, blank=True)

    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)
    status = models.CharField(_("Progress Status"), max_length=20, choices=DECISIONS, default=Decision.NEW.value)
    is_escalated = models.BooleanField(_("Escalated?"), default=False)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rev_reviewer", null=True, blank=True, on_delete=models.SET_NULL)
    res_content = models.TextField(_("Review result"), null=True, blank=True)

    # attachment=models.FileField(_("attachment"), upload_to='reviews', null=True, blank=True)

    # CBUs = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)
    # CBUs  = models.ManyToManyField(CBU, blank=True)
    # dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.PROTECT)

    created_on = models.DateField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rev_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rev_updated_by", null=True, on_delete=models.SET_NULL)

    class Meta:
        #https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#custom-permissions
        permissions = [
            (ReqTypes.PRO.value, 'ReqType - ' + ReqTypes.PRO.value[3:]),
            # (ReqTypes.SEC.value, 'ReqType - ' + ReqTypes.SEC.value[3:]),
            # (ReqTypes.INF.value, 'ReqType - ' + ReqTypes.INF.value[3:]),
            # (ReqTypes.APP.value, 'ReqType - ' + ReqTypes.APP.value[3:]),
            # (ReqTypes.MGT.value, 'ReqType - ' + ReqTypes.MGT.value[3:]),
        ]        
        ordering = ['-updated_on']

	# used while managing models from terminal
    def __str__(self):
        return self.title

    # @property
    # def CBU_str(self):
    #     return " ,".join(p.name for p in self.CBUs.all())

class ReviewLog(models.Model):
    class Meta:
        verbose_name = _("Review Item")
        verbose_name_plural = _("Review Items")

    task = models.ForeignKey(Review, on_delete=models.CASCADE)
    logdt = models.DateField(_("Date"), null=True, blank=True, default=date.today)
    item_description = models.CharField(_("description"), max_length=200)
    is_done = models.BooleanField(_("done?"), default=False)

    def __str__(self):
        return self.item_description
