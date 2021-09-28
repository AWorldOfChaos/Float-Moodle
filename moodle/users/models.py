from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.contrib.auth.models import User


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


class Assignment(models.Model):
    problem_statement = "To be added"
    course = ForeignKey(Course, on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    dictionary_of_marks = {}

    def upload_marks(self, marksDictionary):
        pass

    def extend_deadline(self, newdeadline):
        pass

    def download_submmissions(self):
        pass

    def modify_problem_statement(self):
        pass


class Submission(models.Model):
    assignment = ForeignKey(Assignment, on_delete=models.CASCADE)
    data = "this is my submission"
