from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CourseForm, Assignmentform, Removeinstructor, Removestudent, SubmissionForm,\
                   Feedback
from .models import Course, Profile, Assignment, Submission, Student, Instructor, Invite, FeedbackModel, Evaluation
from django.contrib.auth.models import User
from django.views import View
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage
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
    user = request.user
    profile = user.UserProfile
    all_student_courses = []
    students = profile.student_set.all()
    for student in students:
        all_student_courses.append(student.course)

    all_instructor_courses = []
    instructors = profile.instructor_set.all()
    for instructor in instructors:
        all_instructor_courses.append(instructor.course)

    all_head_courses = []
    head_instructors = user.course_set.all()
    for head_instructor in head_instructors:
        all_head_courses.append(head_instructor)

    if request.method == "POST":
            join_code = request.POST['join_code']
            print(join_code)
            course = Course.objects.get(join_code=join_code)
            if course:
                course_code = course.course_code
                user = request.user
                profile = user.UserProfile
                stud2 = profile.student_set.filter(course=course)
                if not stud2:
                    student = Student(obj=profile, course=course)
                    student.save()
                return redirect('/courses/{}/'.format(course_code))
            else:
                context = {'user': user,
                           'profile': profile,
                           'all_student_courses': all_student_courses,
                           'all_instructor_courses': all_instructor_courses,
                           'all_head_courses': all_head_courses}
                return render(request, 'users/dashboard.html', context=context)

    context = {'user': user,
               'profile': profile,
               'all_student_courses': all_student_courses,
               'all_instructor_courses': all_instructor_courses,
               'all_head_courses': all_head_courses}
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


@login_required
def assignments(request, course_code, assignment_id):
    course = Course.objects.get(course_code=course_code)
    profile = request.user.UserProfile
    stud2 = profile.student_set.filter(course=course)
    ins2 = profile.instructor_set.filter(course=course)
    head_instructor = course.head_instructor
    headProfile = head_instructor.UserProfile
    students = course.student_set.all()
    instructors = course.instructor_set.all()
    assignment = Assignment.objects.get(id=assignment_id)
    form1 = SubmissionForm()
    form2 = Feedback()
    if stud2:
        filename = assignment.problem_statement.name.split('/')[-1]
        filePath = settings.MEDIA_URL + course_code + "/assignments/" + filename
        if assignment.graded:
            if assignment.submission_set.filter(student=stud2[0]):
                submission_instance = assignment.submission_set.get(student=stud2[0])
                marks = submission_instance.marks
                marks = "You got " + str(marks) + " marks."
            else:
                marks = "Not submitted. You got 0 marks."
        else:
            marks = "not graded yet"

        if request.method == "POST":
            if "submission" in request.POST:
                form = SubmissionForm(request.POST, request.FILES)
                if form.is_valid():
                    submission = Submission(student=Student.objects.get(obj=profile, course=course), assignment=assignment,
                                            submittedFile=request.FILES['solution'])
                    submission.save()
                    return redirect('/courses/{}/'.format(course_code))
                form1 = SubmissionForm
                return render(request, 'assignments/assignment_view.html', {'submissionForm': form1, 'filePath':filePath})

        return render(request, 'assignments/assignment_view.html', {'submissionForm': form1, 'filePath':filePath, 'marks':marks})

    elif request.user == head_instructor:
        submissions = assignment.submission_set.all()
        if request.method == "POST":
            form = Feedback(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['feedback']
                evaluation = Evaluation(assignment=assignment, csv_file=csv_file)
                evaluation.save()
                evaluation.evaluate()
                return redirect('/courses/{}/'.format(course_code))
            form2 = Feedback()

        return render(request, 'assignments/head_instructors_view.html', {"submissions":submissions, "feedbackForm":form2})


@login_required(login_url="/login/")
def course_view(request, course_code):
    course = Course.objects.get(course_code=course_code)
    students = course.student_set.all()
    prof2 = request.user.UserProfile
    stud2 = prof2.student_set.filter(course=course)
    ins2 = prof2.instructor_set.filter(course=course)
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
                    newAssignment = Assignment(name=request.POST['name'], course=course,
                                               problem_statement=request.FILES['problem'])
                    newAssignment.save()
                    return redirect('assignments', course_code=course.course_code, assignment_id=newAssignment.id)

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                messages.success(request, "successfully added an assignment")
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all()})

            elif "remove_student_form" in request.POST:
                form = Removestudent(request.POST)
                if form.is_valid():
                    student_profile = Profile.objects.get(roll_number=form.cleaned_data.get('roll_no'))
                    student = Student.objects.filter(obj=student_profile, course=course)[0]
                    student.delete()

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                messages.success(request, "successfully removed a student")
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all()})

            elif "remove_instructor_form" in request.POST:
                form = Removeinstructor(request.POST)
                if form.is_valid():
                    instructor_profile = Profile.objects.get(roll_number=form.cleaned_data.get('roll_no'))
                    instructor = Instructor.objects.filter(obj=instructor_profile, course=course)[0]
                    instructor.delete()

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                messages.success(request, "successfully removed an instructor")
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all()})

            form1 = Assignmentform()
            form2 = Removeinstructor()
            form3 = Removestudent()

        return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors,
                                                                 'assignment_form': form1,
                                                                 "remove_student_form": form3,
                                                                 "remove_instructor_form": form2,
                                                                 'assignments': course.assignment_set.all()})
    elif stud2:

        return render(request, 'courses/course_view_stud.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors,
                                                                 'assignments': course.assignment_set.all()})
    elif ins2:
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
    stud2 = profile.student_set.filter(course=course)
    if not stud2:
        student = Student(obj=profile, course=course)
        student.save()
    return redirect('/courses/{}/'.format(course_code))


@login_required(login_url="/login/")
def invite(request, course_code):
    course = Course.objects.get(course_code=course_code)
    user = request.user
    if user == course.head_instructor:
        users = User.objects.all()
        all_users = []
        for curr_user in users:
            all_users.append(curr_user.UserProfile)
        return render(request, 'courses/invite_page.html', {'all_users': all_users})
    else:
        return redirect('/courses/{}/'.format(course_code))


@login_required(login_url="/login/")
def send_invite(request, course_code, profile_name):
    course = Course.objects.get(course_code=course_code)
    user = request.user
    profile = Profile.objects.get(name=profile_name)
    if user == course.head_instructor:
        inv = Invite(course=course, profile=profile)
        inv.save()
    else:
        return redirect('/courses/{}/'.format(course_code))


@login_required(login_url="/login/")
def invite_view(request):
    user = request.user
    invites = user.UserProfile.invite_set.all()
    all_invites = []
    for curr_invite in invites:
        all_invites.append(curr_invite.course.course_code)
    return render(request, 'users/invite_view.html', {'all_invites': all_invites})


@login_required(login_url="/login/")
def invite_accept(request, course_code):
    course = Course.objects.get(course_code=course_code)
    user = request.user
    ins = Instructor(obj=user.UserProfile, course=course)
    ins.save()
    # Need to remove student user as required
    # Need to delete invite from invite_list
    # Need to implement feature to delete invite
    return redirect('/courses/{}/'.format(course_code))


@login_required(login_url="/login/")
def grades(request, course_code):
    course = Course.objects.get(course_code=course_code)
    students = course.student_set.all()
    prof2 = request.user.UserProfile
    stud2 = prof2.student_set.filter(course=course)
    ins2 = prof2.instructor_set.filter(course=course)
    head_instructor = course.head_instructor
    profile = head_instructor.UserProfile
    instructors = course.instructor_set.all()
    if request.user == head_instructor or ins2:
        # show all grades
        pass
    elif stud2:
        # show only own grades
        pass
    else:
        return redirect('/courses/{}/'.format(course_code))
