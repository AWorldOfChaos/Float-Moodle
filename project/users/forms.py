from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50)
    roll_number = forms.IntegerField()
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2','name', 'email','roll_number' ]