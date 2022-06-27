# from django import forms
# from django.forms import ModelForm
# from django.utils.translation import gettext_lazy as _

# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Submit, Row, Column

# from psm.models import Project
 
# class ProjectRequestForm(ModelForm):
#     class Meta:
#         model = Project
#         fields = [  'title', 'pm', 'year', 'CBU',
#                     'asis', 'img_asis', 'tobe', 'img_tobe',
#                     'description', 'consider', 
#                     'quali', 'quant', 'est_cost', 'resource',
#                     'p_ideation', 'p_plan_b', 'p_kickoff', 'p_design_b', 'p_uat_b', 'p_launch', 'p_close',
#                 ]
#         widgets = {
#             'asis':         forms.Textarea(attrs={'rows':7, 'cols':80}),
#             'tobe':         forms.Textarea(attrs={'rows':7, 'cols':80}),
#             'description':  forms.Textarea(attrs={'rows':5, 'cols':80}),
#             'consider':     forms.Textarea(attrs={'rows':5, 'cols':80}),
#             'quali':        forms.Textarea(attrs={'rows':3, 'cols':80}),
#             'quant':        forms.Textarea(attrs={'rows':3, 'cols':80}),
#             'resource':     forms.Textarea(attrs={'rows':2, 'cols':80}),
#             }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Submit('submit', 'Submit', css_class='form-group float-end'),
#             Row(
#                 Column('title',    css_class='form-group col-md-6 mb-0'),
#                 Column('year',     css_class='form-group col-md-2 mb-0'),
#                 Column('pm',       css_class='form-group col-md-4 mb-0'),
#             ),
#             'CBU',
#             Row(
#                 Column('asis',     css_class='form-group col-md-6 mb-0 prj-main'),
#                 Column('tobe',     css_class='form-group col-md-6 mb-0 prj-main'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('img_asis',    css_class='form-group col-md-6 mb-0'),
#                 Column('img_tobe',    css_class='form-group col-md-6 mb-0'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('description', css_class='form-group col-md-6 mb-0 prj-sub1'),
#                 Column('consider',    css_class='form-group col-md-6 mb-0 prj-sub1'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('quali',     css_class='form-group col-md-6 mb-0 prj-sub2'),
#                 Column('quant',     css_class='form-group col-md-6 mb-0 prj-sub2'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('est_cost',    css_class='form-group col-md-6 mb-0 prj-sub3'),
#                 Column('resource',    css_class='form-group col-md-6 mb-0 prj-sub3'),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column('p_ideation',  id='p_ideation', css_class='form-group mb-0'),
#                 Column('p_plan_b',    id='p_plan_b', css_class='form-group mb-0'),
#                 Column('p_kickoff',   id='p_kickoff', css_class='form-group mb-0'),
#                 Column('p_design_b',  id='p_design_b', css_class='form-group mb-0'),
#                 Column('p_uat_b',     id='p_uat_b', css_class='form-group mb-0'),
#                 Column('p_launch',    id='p_launch', css_class='form-group mb-0'),
#                 Column('p_close',     id='p_close', css_class='form-group mb-0'),
#                 css_class='form-row'
#             ),
        
#         )