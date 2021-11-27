from django.contrib import admin
from users.models import Profile, Course, Assignment, Submission, Evaluation, Post, Replie, Conversations
# Register your models here.

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Evaluation)
admin.site.register(Post)
admin.site.register(Replie)
admin.site.register(Conversations)
#admin.site.register(Replie)