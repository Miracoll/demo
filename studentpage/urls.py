from django.urls import path
from . import views

urlpatterns = [
    # path('student/result/<str:pk>/', views.result, name='result'),
    path('',views.studentdash, name='studentdash'),
    path('login/',views.loginuser, name='signin'),
    # # path('student/login/',views.loginuser, name='signin'),
    path('logout/', views.logoutuser, name='signout'),
    path('password/recovery/', views.forgetPassword, name='student_forget_password'),
    path('check-result/',views.checkresult, name='resultchecker'),
    path('show/tuition/detail/', views.showtuition, name='showtuition'),
    path('print/tuition/receipt/', views.tuitionreceipt, name='tuitionreceipt'),
    path('check-result/<str:pk>/<str:term>/',views.displayresult, name='studentresult'),
    path('printout/<str:pk>/<str:term>/',views.displayresultpdf, name='studentresult_pdf'),
    path('result/printout/<uuid:pk>/<str:term>/<str:getgroup>/<str:getarm>/<uuid:getsession>/',views.showResult, name='show_result'),
    path('annual/result/printout/<uuid:pk>/<str:term>/<str:getgroup>/<str:getarm>/<uuid:getsession>/',views.showAnnualResult, name='show_annual_result'),
    path('hostel/',views.hostel, name='hostel'),
    path('show/hostel/detail/<str:pk>/', views.showhostel, name='showhostel'),
    path('print/hostel/receipt/', views.hostelreceipt, name='hostelreceipt'),
    path('payment/history/', views.history, name='history'),
    path('broadcast/',views.news,name='student_news'),
    path('broadcast/<str:reference>',views.single_news,name='single_news'),
    path('change-password/',views.ChangePassword.as_view(),name='change_password'),
    path('profile/',views.profile,name='student_profile'),
    path('register/courses',views.registerCourses,name='student_course_register'),
    path('add/course/<str:sub>/<str:ref>/',views.addCourses,name='student_add_course'),
    path('remove/course/<str:ref>/',views.removeCourses,name='student_remove_course'),
]