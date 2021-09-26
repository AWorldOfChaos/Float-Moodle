from django.contrib import admin
from users.models import Profile, Course, Assignment, Submission
# Register your models here.

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)

