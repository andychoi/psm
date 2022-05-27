from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date

from common.models import CBU, Dept, Div, STATE3, STATUS, Status, PRIORITIES, Priority, REVIEWTYPES, ReviewTypes


# Create your models here.

# creating an django model class
class Review(models.Model):

    reviewtype = models.CharField(_("Review Type"), max_length=40, choices=REVIEWTYPES, default=ReviewTypes.PRO.value)
    project = models.ForeignKey('psm.Project', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)

    priority = models.CharField(_("priority"), max_length=20, choices=PRIORITIES, default=Priority.NORMAL.value)
    status = models.CharField(_("Progress Status"), max_length=20, choices=STATUS, default=Status.GREEN.value)

    # related = models.ManyToManyField( to='common.Dept', related_name='related_depts')
    # related = models.TextField(_("Related teams"))
    content = models.TextField(_("Action items/notes"), null=True, blank=True)

    proc_start = models.DateField(_("Review DESIRED start date"), null=True, blank=True)
    onboaddt = models.DateField(_("Vendor DESIRED onboarding date"), null=True, blank=True)

    is_escalated = models.BooleanField(_("Escalated?"), default=False)
    state = models.CharField(_("PM Requested?"), max_length=10, choices=STATE3, default=0)

    CBU = models.ForeignKey(CBU, blank=True, null=True, on_delete=models.PROTECT)
    dept = models.ForeignKey(Dept, blank=True, null=True, on_delete=models.PROTECT)
    div = models.ForeignKey(Div, blank=True, null=True, on_delete=models.PROTECT)

    created_on = models.DateField(_("created at"), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proc_created_by", null=True, on_delete=models.SET_NULL)
    updated_on = models.DateTimeField(_("last updated"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proc_updated_by", null=True, on_delete=models.SET_NULL)


	# meta for the class
    class Meta:
        ordering = ['-updated_on']
	# used while managing models from terminal
    def __str__(self):
        return self.title

class ReviewLog(models.Model):
    class Meta:
        verbose_name = _("Action Item")
        verbose_name_plural = _("Action Items")

    task = models.ForeignKey(Review, on_delete=models.CASCADE)
    logdt = models.DateField(_("Date"), null=True, blank=True, default=date.today)
    item_description = models.CharField(_("description"), max_length=200)
    is_done = models.BooleanField(_("done?"), default=False)

    def __str__(self):
        return self.item_description