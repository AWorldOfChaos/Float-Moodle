from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.utils.timezone import now


# Create your models here.


class Profile(models.Model):
    name = models.CharField(max_length=50)
    roll_number = models.IntegerField()
    email = models.EmailField()
    user = OneToOneField(User, on_delete=models.CASCADE, related_name="UserProfile")

    def __str__(self):
        return self.name

 #   def create_course(self, course_name, description):
 #       new_course = Course(course_name=course_name,head_instructor=self.user, description=description)
 #       new_course.save()


class Course(models.Model):
    course_name = models.CharField(max_length=200)
    head_instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    course_code = models.CharField(max_length=10, unique=True)
    join_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.course_code

    def add_assignment(self, deadline):
        course_instance = Course.objects.filter(course_name= self.course_name)
        new_assignment = Assignment(course= course_instance, deadline=deadline)
        new_assignment.save()


class Student(models.Model):
    obj = ForeignKey(Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.obj.name


class Instructor(models.Model):
    obj = ForeignKey(Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.obj.name


def upload_path(instance, filename):
    return "{}/assignments/{}".format(instance.course.course_code, filename)


class Assignment(models.Model):
    name = models.CharField(max_length=50, unique=True, default="No name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    problem_statement = models.FileField(upload_to=upload_path, default=None)
    graded = models.BooleanField(default=False)


def grades_path(instance, filename):
    return "{}/grades/{}".format(instance.assignment.course.course_code, filename)


class Evaluation(models.Model):
    assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE)
    csv_file = models.FileField(upload_to=grades_path, default=None)

    def evaluate(self):
        # filePath = "/media/" + self.csv_file.name
        filePath = os.path.join(settings.MEDIA_ROOT, self.csv_file.name)
        file_instance = open(filePath, 'r')
        for lines in file_instance.readlines():
            lines = lines.split(",")
            roll_number = lines[0]
            marks = lines[1]
            profile = Profile.objects.get(roll_number= roll_number)
            student_instance = self.assignment.course.student_set.filter(obj=profile)[0]
            submission = self.assignment.submission_set.filter(student = student_instance)[0]
            submission.marks = marks
            submission.save()
        self.assignment.graded = True
        self.assignment.save()


def submission_path(instance, filename):
    return "{}/submissions/{}/{}".format(instance.assignment.course.course_code, instance.assignment.name, filename)


class Submission(models.Model):
    student = ForeignKey(Student, on_delete=models.CASCADE, default=None)
    assignment = ForeignKey(Assignment, on_delete=models.CASCADE)
    submittedFile = models.FileField(upload_to=submission_path, default=None)
    marks = models.IntegerField(default=-1)


class FeedbackModel(models.Model):
    student = ForeignKey(Student, on_delete= models.CASCADE, default= None)
    assignment = ForeignKey(Assignment, on_delete=models.CASCADE)
    feedback = models.TextField(default="")


class Invite(models.Model):
    course = ForeignKey(Course, on_delete=models.CASCADE)
    profile = ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.course

class Post(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default='' )
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    post_id = models.AutoField
    post_content = models.CharField(max_length=5000)
    timestamp= models.DateTimeField(default=now)
    
class Replie(models.Model):
    course = ForeignKey(Course, on_delete=models.CASCADE, default='' )
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    reply_id = models.AutoField
    reply_content = models.CharField(max_length=5000) 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default='')
    timestamp= models.DateTimeField(default=now)

class Conversations(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name="firstUser")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name="secondUser")
    convo_id = models.AutoField

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    convo = models.ForeignKey(Conversations, on_delete=models.CASCADE, default=1 )
    message_content = models.CharField(max_length=5000) 
    timestamp= models.DateTimeField(default=now)