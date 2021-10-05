from users.models import Assignment
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from users.models import Course
from django.db import models
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
    problem = forms.FileField(label="Select a File")

class Removestudent(forms.Form):
    roll_no = forms.IntegerField()

class Removeinstructor(forms.Form):
    roll_no = forms.IntegerField()

class JoinCourse(forms.form):
    course_code = forms.IntegerField()
