from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

#lower case for user login
from django.contrib.auth.forms import AuthenticationForm
class MyAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data['username'].lower()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        return self.cleaned_data['username'].lower()


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        # fields = ['name', 'email']
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'u_dept', 'u_team', 'CBU']
