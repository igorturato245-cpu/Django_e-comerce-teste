from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from . import models

class cadastroform(UserCreationForm):
    ...

class loginform(forms.ModelForm):
    ...

class user_updateform(forms.ModelForm):
    ...

class pagamentoform(forms.Form):
    ...