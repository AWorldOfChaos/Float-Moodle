from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import DateInput, NumberInput
from users.models import Course, Assignment
from django.db import models
from django.forms import ModelForm
from django.forms import ModelForm


class UserRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50)
    roll_number = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2','name', 'email','roll_number']


class CourseForm(ModelForm):
    course_code = forms.CharField(max_length=10)
    course_name = forms.CharField(max_length=200)
    join_code = forms.CharField(max_length=10)

    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'join_code']



class Assignmentform(forms.Form):
    name = forms.CharField()
    deadline = forms.DateField(widget=NumberInput(attrs={'type':'date'}))
    weightage = forms.IntegerField()
    problem = forms.FileField(label="Select a File")

class ExtensionForm(forms.Form):
    new = forms.DateField(widget= NumberInput(attrs={'type':'date'}))

class Removestudent(forms.Form):
    roll_no = forms.IntegerField()


class Removeinstructor(forms.Form):
    roll_no = forms.IntegerField()


class SubmissionForm(forms.Form):
    solution = forms.FileField(label="Select a File")


class Feedback(forms.Form):
    feedback = forms.FileField(label="Select a csv file")
