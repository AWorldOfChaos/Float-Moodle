from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CourseForm, Assignmentform, Removeinstructor, Removestudent, SubmissionForm, \
    Feedback, ExtensionForm, Conversationform
from .models import Course, Profile, Assignment, Submission, Student, Instructor, Invite, FeedbackModel, Evaluation, Post, Replie, Conversations, Messages
from django.contrib.auth.models import User
from django.views import View
from django.conf import settings
import os
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from django.core.files.storage import FileSystemStorage
import subprocess
import math
from django.core.mail import send_mail
import json


# Create your views here.

class Data:
    def __init__(self, c, c1, c2):
        self.course = c
        self.count1 = str(c1)
        self.count2 = str(c2)
        if c1 == 0:
            self.percent = 0
        else:
            self.percent = 100*c2/c1


class StudentAssignmentData:
    def __init__(self, s, avg, n):
        self.submission = s
        self.average = avg
        self.name = n


class InstructorAssignmentData:
    def __init__(self, a, avg, var, n, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10):
        self.assignment = a
        self.average = avg
        self.variance = var
        # self.number = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.name = n
        self.y1 = x1
        self.y2 = x2
        self.y3 = x3
        self.y4 = x4
        self.y5 = x5
        self.y6 = x6
        self.y7 = x7
        self.y8 = x8
        self.y9 = x9
        self.y10 = x10


class StatisticData:
    def __init__(self, a, avg, n, var, w):
        self.assignment = a
        self.average = avg
        self.name = n
        self.variance = var
        self.weightage = w


class StudentChartData:

    def __init__(self, data):
        abgC = []
        abC = []
        for i in range(len(data)):
            abgC.append('rgba(75, 192, 192, 0.2)')
            abC.append('rgba(75, 192, 192, 1)')

        self.averagebgColor = json.dumps(abgC)
        self.averageBorderColor = json.dumps(abC)

        abgC = []
        for i in range(len(data)):
            abgC.append('rgba(54, 162, 235, 0.2)')
            abC.append('rgba(54, 162, 235, 1)')

        self.studentbgColor = json.dumps(abgC)
        self.studentBorderColor = json.dumps(abC)

        aN = []
        for i in range(len(data)):
            aN.append(data[i].submission.assignment.name)

        self.assignment_names = json.dumps(aN)

        aD = []
        for i in range(len(data)):
            aD.append(data[i].submission.marks)

        self.data = json.dumps(aD)

        cA = []
        for i in range(len(data)):
            cA.append(data[i].average)

        self.class_average = json.dumps(cA)


class InstructorMeanChart:
    def __init__(self, data):
        m = []
        for i in range(len(data)):
            m.append(data[i].average)
        self.means = json.dumps(m)

        aN = []
        for i in range(len(data)):
            aN.append(data[i].assignment.name)

        self.assignment_names = json.dumps(aN)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            roll_number = form.cleaned_data.get('roll_number')
            profile = Profile(name=name, email=email, roll_number=roll_number,
                              user=User.objects.filter(username=username)[0])
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
    progress = []
    for student in students:
        count1 = 0
        count2 = 0
        for submission in student.submission_set.all():
            count1 += 1
            if submission.submitted:
                count2 += 1
        all_student_courses.append(Data(student.course, count1, count2))

    all_instructor_courses = []
    instructors = profile.instructor_set.all()
    for instructor in instructors:
        all_instructor_courses.append(instructor.course)

    all_head_courses = []
    head_instructors = user.course_set.all()
    for head_instructor in head_instructors:
        all_head_courses.append(head_instructor)

    unsubmittedAssignments = []
    for student in students:
        for submission in student.submission_set.all():
            if not submission.submitted:
                if submission.assignment.is_open():
                    unsubmittedAssignments.append(submission.assignment)

    ungradedAssignments = []
    for course in Course.objects.all():
        if course.head_instructor == user or profile.instructor_set.filter(course=course):
            for assignment in course.assignment_set.all():
                if not assignment.graded:
                    ungradedAssignments.append(assignment)

    if request.method == "POST":
        join_code = request.POST['join_code']
        # print(join_code)
        course = Course.objects.get(join_code=join_code)
        if course:
            course_code = course.course_code
            user = request.user
            profile = user.UserProfile
            stud2 = profile.student_set.filter(course=course)
            if not stud2:
                student = Student(obj=profile, course=course)
                student.save()
                for assignment in course.assignment_set.all():
                    submission = Submission(assignment=assignment, student=student)
                    submission.save()
            return redirect('/courses/{}/'.format(course_code))
        else:
            context = {'user': user,
                       'profile': profile,
                       'all_student_courses': all_student_courses,
                       'all_instructor_courses': all_instructor_courses,
                       'all_head_courses': all_head_courses,
                       'unsubmitted': unsubmittedAssignments,
                       'ungraded': ungradedAssignments}
            return render(request, 'users/dashboard.html', context=context)

    context = {'user': user,
               'profile': profile,
               'all_student_courses': all_student_courses,
               'all_instructor_courses': all_instructor_courses,
               'all_head_courses': all_head_courses,
               'unsubmitted': unsubmittedAssignments,
               'ungraded': ungradedAssignments}
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
            can_grade = form.cleaned_data.get('canGrade')
            can_add = form.cleaned_data.get('canAddAssignment')
            can_remove = form.cleaned_data.get('canRemoveStudents')
            can_extend = form.cleaned_data.get('canExtendDeadline')
            course = Course.objects.create(head_instructor=request.user, course_name=course_name,
                                           course_code=course_code, join_code=join_code, forumActive=True,
                                           canGrade=can_grade, canAddAssignment=can_add,
                                           canRemoveStudents=can_remove, canExtendDeadline=can_extend)
            send_mail('course creation on Moodle', 'you have created a new course on moodle', 'sslproject1000@gmail.com', [request.user.email],
            fail_silently= False)
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
    form3 = ExtensionForm()
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
            if assignment.is_open():
                if "submission" in request.POST:
                    form = SubmissionForm(request.POST, request.FILES)
                    if form.is_valid():
                        submission = stud2[0].submission_set.get(assignment=assignment)
                        submission.submittedFile = request.FILES['solution']
                        submission.submitted = True
                        submission.save()
                        send_mail('course creation on Moodle', 'you have made a submission to an assignment.', 'sslproject1000@gmail.com', [request.user.email],
                        fail_silently= False)
                        return redirect('/courses/{}/'.format(course_code))
                    form1 = SubmissionForm
                    return render(request, 'assignments/assignment_view.html',
                                  {'open': assignment.is_open(), 'submissionForm': form1, 'filePath': filePath,
                                   'active': assignment.active})

                else:
                    return render(request, 'assignments/assignment_view.html',
                                  {'open': assignment.is_open(), 'submissionForm': form1, 'filePath': filePath,
                                   'active': assignment.active})
        return render(request, 'assignments/assignment_view.html',
                      {'open': assignment.is_open(), 'submissionForm': form1, 'filePath': filePath, 'marks': marks,
                       'active': assignment.active})

    elif request.user == head_instructor:
        submissions = assignment.submission_set.all()
        if request.method == "POST":
            if "feedback" in request.POST:
                form = Feedback(request.POST, request.FILES)
                if form.is_valid():
                    csv_file = request.FILES['feedback']
                    evaluation = Evaluation(assignment=assignment, csv_file=csv_file)
                    evaluation.save()
                    evaluation.evaluate()
                    return redirect('/courses/{}/'.format(course_code))

            if "autograde" in request.POST:
                form = Feedback(request.POST, request.FILES)
                if form.is_valid():
                    script_file = request.FILES['feedback']
                    evaluation = Evaluation(assignment=assignment, csv_file=script_file)
                    evaluation.save()
                    filePath = os.path.join(settings.MEDIA_ROOT, evaluation.csv_file.name)
                    for submission in assignment.submission_set.all():
                        filename1 = submission.submittedFile.name.split('/')[-1]
                        filepath1 = os.path.join(settings.MEDIA_ROOT, submission.submittedFile.name)
                        proc = subprocess.Popen(['python', filePath, filepath1], stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT)
                        output = proc.communicate()[0]
                        marks = output.decode('UTF-8')[0]
                        marks = int(marks)
                        marks = marks * assignment.weightage
                        submission.marks = marks
                        submission.save()

                        assignment.graded = True
                        assignment.save()
                    return redirect('/courses/{}/'.format(course_code))

            if "extend" in request.POST:
                assignment.deadline = request.POST['new']
                assignment.save()
            form2 = Feedback()
            form3 = ExtensionForm()

        return render(request, 'assignments/head_instructors_view.html',
                      {"deadline": assignment.deadline, "extensionform": form3, "submissions": submissions,
                       "feedbackForm": form2, 'active': assignment.active})

    elif ins2:
        submissions = assignment.submission_set.all()
        if request.method == "POST":
            if "feedback" in request.POST:
                form = Feedback(request.POST, request.FILES)
                if form.is_valid() and course.canGrade:
                    csv_file = request.FILES['feedback']
                    evaluation = Evaluation(assignment=assignment, csv_file=csv_file)
                    evaluation.save()
                    evaluation.evaluate()
                    return redirect('/courses/{}/'.format(course_code))

            if "autograde" in request.POST:
                form = Feedback(request.POST, request.FILES)
                if form.is_valid() and course.canGrade:
                    script_file = request.FILES['feedback']
                    evaluation = Evaluation(assignment=assignment, csv_file=script_file)
                    evaluation.save()
                    filePath = os.path.join(settings.MEDIA_ROOT, evaluation.csv_file.name)
                    for submission in assignment.submission_set.all():
                        filename1 = submission.submittedFile.name.split('/')[-1]
                        filepath1 = os.path.join(settings.MEDIA_ROOT, submission.submittedFile.name)
                        proc = subprocess.Popen(['python', filePath, filepath1], stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT)
                        output = proc.communicate()[0]
                        marks = output.decode('UTF-8')[0]
                        marks = int(marks)
                        marks = marks * assignment.weightage
                        submission.marks = marks
                        submission.save()

                        assignment.graded = True
                        assignment.save()
                    return redirect('/courses/{}/'.format(course_code))

            if "extend" in request.POST and course.canExtendDeadline:
                assignment.deadline = request.POST['new']
                assignment.save()
            form2 = Feedback()
            form3 = ExtensionForm()

        return render(request, 'assignments/head_instructors_view.html',
                      {"deadline": assignment.deadline, "extensionform": form3, "submissions": submissions,
                       "feedbackForm": form2, 'active': assignment.active})


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
                    newAssignment = Assignment(name=request.POST['name'], weightage=request.POST['weightage'],
                                               deadline=request.POST['deadline'], course=course,
                                               problem_statement=request.FILES['problem'], active=True)
                    newAssignment.save()
                    for student in students:
                        submission = Submission(assignment=newAssignment, student=student)
                        submission.save()
                    return redirect('assignments', course_code=course.course_code, assignment_id=newAssignment.id)

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all(),
                                                                         'forumOn': course.forumActive})

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
                                                                         'assignments': course.assignment_set.all(),
                                                                         'forumOn': course.forumActive})

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
                                                                         'assignments': course.assignment_set.all(),
                                                                         'forumOn': course.forumActive})

            elif "toggle" in request.POST:
                course.forumActive = not course.forumActive
                course.save()
                return render(request, 'courses/course_view_head.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all(),
                                                                         'forumOn': course.forumActive})

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
        form1 = Assignmentform()
        form2 = Removeinstructor()
        form3 = Removestudent()
        if request.method == 'POST':

            if "assignment_form" in request.POST:
                form = Assignmentform(request.POST, request.FILES)
                if form.is_valid() and course.canAddAssignment:
                    newAssignment = Assignment(name=request.POST['name'], weightage=request.POST['weightage'],
                                               deadline=request.POST['deadline'], course=course,
                                               problem_statement=request.FILES['problem'], active=True)
                    newAssignment.save()
                    for student in students:
                        submission = Submission(assignment=newAssignment, student=student)
                        submission.save()
                    return redirect('assignments', course_code=course.course_code, assignment_id=newAssignment.id)

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                return render(request, 'courses/course_view_ins.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all()})

            elif "remove_student_form" in request.POST:
                form = Removestudent(request.POST)
                if form.is_valid() and course.canRemoveStudents:
                    student_profile = Profile.objects.get(roll_number=form.cleaned_data.get('roll_no'))
                    student = Student.objects.filter(obj=student_profile, course=course)[0]
                    student.delete()
                    messages.success(request, "successfully removed a student")

                form1 = Assignmentform()
                form2 = Removeinstructor()
                form3 = Removestudent()
                return render(request, 'courses/course_view_ins.html', {'code': course_code, 'head': profile.name,
                                                                         'all_students': students,
                                                                         'all_instructors': instructors,
                                                                         'assignment_form': form1,
                                                                         "remove_student_form": form3,
                                                                         "remove_instructor_form": form2,
                                                                         'assignments': course.assignment_set.all()})

            form1 = Assignmentform()
            form2 = Removeinstructor()
            form3 = Removestudent()

        return render(request, 'courses/course_view_ins.html', {'code': course_code, 'head': profile.name,
                                                                 'all_students': students,
                                                                 'all_instructors': instructors,
                                                                 'assignment_form': form1,
                                                                 "remove_student_form": form3,
                                                                 "remove_instructor_form": form2,
                                                                 'assignments': course.assignment_set.all()})
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
def send_invite(request, course_code, rollno):
    course = Course.objects.get(course_code=course_code)
    user = request.user
    profile = Profile.objects.get(roll_number=rollno)
    if user == course.head_instructor:
        inv = Invite(course=course, profile=profile)
        inv.save()
        return redirect('/courses/{}/'.format(course_code))
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
    profile = user.UserProfile
    ins2 = profile.instructor_set.filter(course=course)
    if not ins2:
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

    data = []
    data2 = []
    if stud2:
        student = stud2[0]
        total = 0
        total2 = 0

        t = 0
        for assignment in course.assignment_set.all():
            for submission in assignment.submission_set.all():
                t += submission.marks
        avg2 = t/len(course.assignment_set.all()[0].submission_set.all())

        for submission in student.submission_set.all():
            if submission.assignment.course == course:
                total += submission.marks
                total2 += submission.assignment.weightage
        for submission in student.submission_set.all():
            if submission.assignment.course == course:
                assignment2 = submission.assignment
                t = 0
                no = 0
                for submission2 in assignment2.submission_set.all():
                    t += submission2.marks
                    no += 1
                avg = t/no
                n = submission.assignment.name.replace(" ", "")
                data.append(StudentAssignmentData(submission, avg, n))
    else:
        for assignment in course.assignment_set.all():
            n = assignment.name.replace(" ", "")
            y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

            t = 0
            v = 0
            for submission in assignment.submission_set.all():
                t += submission.marks
            avg = t / len(assignment.submission_set.all())
            for submission in assignment.submission_set.all():
                v += (submission.marks - avg) * (submission.marks - avg)
            v = v / len(assignment.submission_set.all())

            for submission in assignment.submission_set.all():
                if submission.marks >= assignment.weightage:
                    y[9] += 1
                else:
                    y[math.floor(10*submission.marks/assignment.weightage)] += 1

            d = InstructorAssignmentData(assignment, avg, v, n, y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7], y[8],
                                         y[9])
            data.append(d)

            # t = 0
            # v = 0
            # for submission in assignment.submission_set.all():
            #     t += submission.marks
            # avg = t/len(assignment.submission_set.all())
            # for submission in assignment.submission_set.all():
            #     v += (submission.marks-avg)*(submission.marks-avg)
            # v = v/len(assignment.submission_set.all())

            n = assignment.name.replace(" ", "")
            data2.append(StatisticData(assignment, avg, n, v, assignment.weightage))

    if request.user == head_instructor or ins2:
        # for assignment in course.assignment_set.all():
        # a = []
        # for submission in assignment.submission_set.all():
        #     a.append(submission.marks)
        # data[assignment.name] = a
        return render(request, 'courses/grades.html', {'assignments': data, 'assignments2': data2, 'is_head': True, 'is_stud': False, 'Instructor_Mean_Chart': InstructorMeanChart(data),})
    elif stud2:
        student = stud2[0]
        # for submission in student.submission_set.all():
        #     if submission.assignment.course == course:
        #         data[submission.assignment.name] = submission.marks
        return render(request, 'courses/grades.html', {'assignments': data, 'is_stud': True, 'is_head': False, 'length': len(course.assignment_set.all()), 'total': total, 'total2': total2, 'avg2': avg2, 'Student_graph': StudentChartData(data)})
    else:
        return redirect('/courses/{}/'.format(course_code))


def cli(request):
    while 1:
        user_input = prompt('>',
                            history=FileHistory('history.txt'),
                            auto_suggest=AutoSuggestFromHistory(),
                            )
        if user_input != 'q':
            print(user_input)
        else:
            break

    return redirect('/')


@login_required(login_url="/login/")
def forum(request, course_code):
    profile = Profile.objects.all()
    course = Course.objects.get(course_code=course_code)
    print(course.forumActive)
    if course.forumActive:
        if request.method == "POST":
            user = request.user
            content = request.POST.get('content','')
            post = Post(user1=user, post_content=content, course=course)
            post.save()
            alert = True
            return render(request, "forum/forum.html", {'alert': alert})
        # posts = Post.objects.filter().order_by('-timestamp')
        return render(request, "forum/forum.html", {'posts': course.post_set.all().order_by('-timestamp'), 'code': course_code})
    else:
        return redirect('/courses/{}/'.format(course_code))


@login_required(login_url="/login/")
def discussion(request, myid, course_code):
    post = Post.objects.filter(id=myid).first()
    replies = Replie.objects.filter(post=post)
    course = Course.objects.get(course_code=course_code)
    if request.method == "POST":
        user = request.user
        desc = request.POST.get('desc','')
        post_id = request.POST.get('post_id','')
        reply = Replie(user=user, reply_content=desc, post=post, course=course)
        reply.save()
        alert = True
        return render(request, "forum/discussion.html", {'alert':alert})
    return render(request, "forum/discussion.html", {'post':post, 'replies':replies, 'code': course_code})


@login_required(login_url="/login/")
def convos(request):
    profile = Profile.objects.all()
    user = request.user
    convos = Conversations.objects.filter(user1=user)
    convos2 = Conversations.objects.filter(user2=user)

    form = Conversationform()
    if request.method == "POST":
        form1 = Conversationform(request.POST)
        if form1.is_valid():
            user1 = request.user
            user2name = request.POST.get('Name')
            print(user2name)
            user2 = Profile.objects.get(name=user2name).user
            if user2:
                convo = Conversations(user1=user1, user2=user2)
                convo.save()
        form = Conversationform()
        return render(request, "conversations/conversations.html", {'convos': convos, 'convos2': convos2, 'form': form})
    else:
        return render(request, "conversations/conversations.html", {'users': profile, 'convos': convos, 'convos2': convos2, 'form': form})
    # return render(request, "conversations/conversations.html", {'users': profile, 'convos': convos, 'convos2': convos2, 'form': form})


@login_required(login_url="/login/")
def dm(request, myid):
    convo = Conversations.objects.filter(id=myid).first()
    messages = Messages.objects.filter(convo=convo)
    if request.method == "POST":
        user = request.user
        desc = request.POST.get('desc', '')
        convo_id = request.POST.get('convo_id', '')
        message = Messages(user=user, message_content=desc, convo=convo)
        message.save()
        alert = True
        return render(request, "conversations/messages.html", {'alert':alert})
    return render(request, "conversations/messages.html", {'convo': convo, 'messages': messages})
