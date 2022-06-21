from django import forms

from .models import ResourcePlan


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PlanCreateForm(BaseForm, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = ResourcePlan
        fields = ['date', 'title' ]


class PlanEditForm(BaseForm, forms.ModelForm):

    class Meta:
        model = ResourcePlan
        fields = ['date', 'title', 'allocation' ]