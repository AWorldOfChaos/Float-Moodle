from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import Course, Profile, Assignment, Submission
from django.contrib.auth.models import User
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            roll_number = form.cleaned_data.get('roll_number')
            profile = Profile(name=name, email=email, roll_number=roll_number, user=User.objects.filter(username=username)[0])
            profile.save()

            messages.success(request, f'Your account has been created!')
            return redirect('login')

    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def home(request):
    context = {}
    return render(request, 'users/home.html', context=context)  