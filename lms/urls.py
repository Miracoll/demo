from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('not-found', views.error404, name='error404'),
    path('login/', views.loginuser, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('user/profile/', views.userprofile, name='userprofile'),
    # path('user/profile/<str:pk>/', views.userprofile, name='profile'),
    path('change-password/',views.changepassword,name='staff_change_password'),
    path('set-password/<str:ref>/',views.setPassword,name='set-password'),
    path('update-info/<str:ref>/',views.updateInfo,name='update-info'),
    path('need-help',views.need_help,name='needhelp'),


    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='application/password_reset.html'), name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='application/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='application/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='application/password_reset_complete.html'), name='password_reset_complete'),
]