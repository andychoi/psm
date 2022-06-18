from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Tag

# 
# https://stackoverflow.com/questions/22002861/booleanfield-checkbox-not-render-correctly-with-crispy-forms-using-bootstrap
#
class PostForm(forms.ModelForm):
        
    # choice = forms.ModelMultipleChoiceField(label=_('tags'),        widget=forms.CheckboxSelectMultiple(),required=False,
    #                                     queryset=Tag.objects.all())
    # def __init__(self, *args, **kwargs):
    #     pass
        # self.helper = FormHelper()
        # self.helper.layout = Layout(

                # Field('name', css_class='input-xlarge'),
                # Field('email', css_class='input-xlarge'),
                # Field('phone_number', css_class='input-xlarge'),
                # Field('message', rows="3", css_class='input-xlarge'),
                # PrependedText('tags', ''),
                # FormActions(
                #     Submit('submit', _('Submit'), css_class="btn-primary")
                # )
            # )
    class Meta:
        model = Post
        fields = "__all__"  
        # fields = ['title', 'content', 'image', 'private', 'featured', 'tags']
        widgets = {
            'content':  forms.Textarea(attrs={'class': 'editable medium-editor-textarea'}),
            'tags':     forms.CheckboxSelectMultiple,
        }
