from django.contrib import admin
from users.models import *
# Register your models here.

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Evaluation)
admin.site.register(Post)
admin.site.register(Reply)

