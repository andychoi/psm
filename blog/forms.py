from django import forms
from .models import Post

# userd by crispy form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'private', 'featured', 'tags']
        # fields = ['title', 'content', 'image', 'tags', 'featured', 'private']

        widgets = {
            'content': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'})
        }
