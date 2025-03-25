from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance, name='attendance'),
    path('get/students/', views.before_attendance, name='before_attendance'),
    path('all/students/<str:group>/<str:arm>/', views.admin_attendance, name='admin_attendance'),
    path('present/<str:id>/', views.present, name='pattendance'),
    path('absent/<str:id>/', views.absent, name='aattendance'),
    path('unlock/', views.unlockattendance, name='unlock'),
]