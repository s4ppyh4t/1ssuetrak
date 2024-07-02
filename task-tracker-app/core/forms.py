from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from issues.models import IssueOwner

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class IssueOwnerForm(forms.ModelForm):
    class Meta:
        model = IssueOwner
        fields = ("user", "profile_img")

    