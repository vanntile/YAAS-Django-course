from django import forms
from django.forms import widgets


class CreateSignupForm(forms.Form):
    email = forms.CharField(widget=widgets.EmailInput)
    username = forms.CharField(max_length=64)
    password = forms.CharField(widget=widgets.PasswordInput)

