from django.conf import settings
from django.urls import path

from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('about/', views.about),
    path('create/', views.course_create, name='create_course'),
    path('courses/<str:course_code>/', views.course_view),
    # path('join/<str:course_code>/', views.join_course),
    path('courses/<str:course_code>/invite/', views.invite),
    path('courses/<str:course_code>/invite/<str:profile_name>', views.send_invite),
    path('invites/', views.invite_view, name='view_invites'),
    path('invites/<str:course_code>/', views.invite_accept),
    path('courses/<str:course_code>/assignments/<int:assignment_id>', views.assignments, name='assignments')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
