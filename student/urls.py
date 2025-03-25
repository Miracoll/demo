from django.urls import path
from . import views

urlpatterns = [
    path('', views.student, name='student'),
    path('entry/', views.getstudent, name='get_student'),
    path('registered-student/<str:pk>/', views.managestudent, name='manage_student'),
    path('transfer/', views.transferstudent, name='transfer_student'),
    path('disable/', views.disablestudent, name='disable_student'),
    path('enable/', views.enablestudent, name='enable_student'),
    path('edit-registraion-number/', views.editreg, name='edit_reg'),
    path('result/', views.getstudentresult, name='get_result'),
    path('reset-student-password/',views.resetstudentpassword,name='studentpasswordreset'),
    path('get-datasheet/', views.datasheet, name='select-datasheet'),
    path('datasheet/<str:ref>/', views.getDatasheet, name='get-datasheet'),
    path('print/datasheet/', views.printDatasheet, name='print-datasheet'),
    path('print/subject-list/', views.printSujectList, name='print-subject-list'),
    path('course/register/get/', views.getStudentRegisterCourse, name='get-student-register-course'),
    path('course/register/<str:ref>/', views.registerCourse, name='register-course'),
    path('add/course/<str:sub>/<str:ref>/',views.addCourses,name='admin-add-course'),
    path('remove/course/<str:ref>/',views.removeCourses,name='admin-remove-course'),
    path('unlock/course', views.unlockCourseRegister, name='unlock-course'),
    path('fix-2024-2025-first-term-result/', views.fix20242025FirstTermResult, name='fix-2024-result'),
]