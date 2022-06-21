from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserForm(forms.Form):
    id = forms.CharField(label="Enter ID ",max_length=50)