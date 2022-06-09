from django import forms
from django.utils.translation import gettext_lazy as _
 
# creating a form
# class ProjectPlanForm(forms.Form):
#     # specify fields for model

#     title = forms.CharField(_("title"), max_length=200)
#     # type = forms.CharField(_("type"), max_length=20, choices=PRJTYPE, default=PrjType.UNC.value)
#     # year = forms.PositiveIntegerField(_("Year"), default=current_year(), validators=[MinValueValidator(2014), max_value_current_year])
#     # strategy = forms.ManyToManyField(Strategy, blank=True, related_name="projects")
#     # program = forms.ForeignKey(Program, blank=True, null=True, on_delete=forms.PROTECT)
#     # is_internal = forms.BooleanField(_("Internal project"), default=False)
#     # is_agile = forms.BooleanField(_("Agile project"), default=False)
#     # is_unplanned = forms.BooleanField(_("Unplanned project"), default=False)

#     # CBUs  = forms.ManyToManyField(CBU, blank=True, related_name="projects")
#     # CBUpm = forms.ForeignKey(Profile, related_name='cbu_pm', verbose_name=_('CBU PM'), on_delete=forms.SET_NULL, null=True, blank=True)
#     # team = forms.ForeignKey(Team, blank=True, null=True, on_delete=forms.PROTECT)
#     # dept = forms.ForeignKey(Dept, blank=True, null=True, on_delete=forms.PROTECT)
#     # div = forms.ForeignKey(Div, blank=True, null=True, on_delete=forms.PROTECT)

#     description = forms.TextField(_("description"), max_length=2000, null=True, blank=True)

#     asis        = forms.TextField(_("As-Is"), max_length=2000, null=True, blank=True)
#     tobe        = forms.TextField(_("To-Be"), max_length=2000, null=True, blank=True)
#     objective   = forms.TextField(_("Objective"), max_length=2000, null=True, blank=True)
#     consider    = forms.TextField(_("Consideration"), max_length=1000, null=True, blank=True)
#     quali       = forms.TextField(_("Qualitative benefit"), max_length=1000, null=True, blank=True)
#     quant       = forms.TextField(_("Quantitative benefit"), max_length=1000, null=True, blank=True)
#     resource    = forms.TextField(_("Quantitative benefit"), max_length=500, null=True, blank=True)
#     img_asis    = forms.ImageField(upload_to='project/%Y', null=True, blank=True)   
#     img_tobe    = forms.ImageField(upload_to='project/%Y', null=True, blank=True)  
