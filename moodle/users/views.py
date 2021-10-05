from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CourseForm, Assignmentform, Removeinstructor, Removestudent, JoinCourse
from .models import Course, Profile, Assignment, Submission, Student, Instructor
from django.contrib.auth.models import User
from django.views import View
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


def about(request):
    return render(request, template_name='users/about.html')


@login_required(login_url='/login/')
def home(request):
    context = {}
    return render(request, 'users/dashboard.html', context=context)


@login_required(login_url='/login/')
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            # form.save()
            course_code = form.cleaned_data.get('course_code')
            course_name = form.cleaned_data.get('course_name')
            join_code = form.cleaned_data.get('join_code')
            course = Course.objects.create(head_instructor=request.user, course_name=course_name,
                                           course_code=course_code, join_code=join_code)
            course.save()
            return redirect('/courses/{}/'.format(course_code))
    else:
        form = CourseForm()
    return render(request, 'courses/create.html', {'form': form})


@login_required(login_url="/login/")
def course_view(request, course_code):
    course = Course.objects.get(course_code=course_code)
    students = course.student_set.all()
    prof2 = request.user.UserProfile
    stud2 = None
    ins2 = None
    if prof2.student_set.all():
        stud2 = prof2.student_set.all()[0]
    if prof2.instructor_set.all():
        ins2 = prof2.instructor_set.all()[0]
    head_instructor = course.head_instructor
    profile = head_instructor.UserProfile
    instructors = course.instructor_set.all()
    if request.user == head_instructor:
        form1 = Assignmentform()
        form2 = Removeinstructor()
        form3 = Removestudent() 
        if request.method == 'POST':
            
            if "assignment_form" in request.POST:
                form = Assignmentform(request.POST, request.FILES)
                if form.is_valid():
                    newAssignment = Assignment(course=course, problem_statement=request.FILES['problem'])
                    newAssignment.save()
                    
                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                messages.success(request, "successfully added an assignment")
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors, 'assignment_form':form1, "assignment_form":form1,
                                                                 "remove_student_form":form3, "remove_instructor_form":form2})

            elif "remove_student_form" in request.POST:
                form = Removestudent(request.POST)
                if form.is_valid():
                    student_profile = Profile.objects.get(roll_number= form.cleaned_data.get('roll_no'))
                    student = Student.objects.filter(obj=student_profile, course=course)[0]
                    student.delete()

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                messages.success(request, "successfully removed a student")
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors, 'assignment_form':form1, "assignment_form":form1,
                                                                 "remove_student_form":form3, "remove_instructor_form":form2})

            
            elif "remove_instructor_form" in request.POST:
                form = Removeinstructor(request.POST)
                if form.is_valid():
                    instructor_profile = Profile.objects.get(roll_number= form.cleaned_data.get('roll_no'))
                    instructor = Instructor.objects.filter(obj=instructor_profile, course=course)[0]
                    instructor.delete()
                
                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                messages.success(request, "successfully removed an instructor")
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors, 'assignment_form':form1, "assignment_form":form1,
                                                                 "remove_student_form":form3, "remove_instructor_form":form2})

                
            form1 = Assignmentform()
            form2 = Removeinstructor()
            form3 = Removestudent()

        return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors, 'assignment_form':form1, "assignment_form":form1,
                                                                 "remove_student_form":form3, "remove_instructor_form":form2})
    elif stud2 in students:
        
        return render(request, 'courses/course_view_stud.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors,
                                                                 'assignments':course.assignment_set.all()})
    elif ins2 in instructors:
        return render(request, 'courses/course_view_ins.html', {'code': course_code, 'head': profile.name,
                                                                'all_students': students,
                                                                'all_instructors': instructors})
    else:

        return render(request, 'courses/course_view_not.html', {'code': course_code, 'head': profile.name,
                                                                'all_students': students,
                                                                'all_instructors': instructors})


@login_required(login_url="/login/")
def join_course(request, course_code):
    course = Course.objects.get(course_code=course_code)
    user = request.user
    profile = user.UserProfile
    student = Student(obj=profile, course=course)
    student.save()
    return redirect('/courses/{}/'.format(course_code))
