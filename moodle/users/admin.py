from django.contrib import admin
from users.models import Instructor, Profile, Course, Assignment, Student, Submission
# Register your models here.

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Student)
admin.site.register(Instructor)

