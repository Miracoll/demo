from django.urls import path
from . import views

urlpatterns = [
    path('get-student/', views.getStudent, name='parent-get-student'),
    path('register-parent/<str:ref>', views.registerParent, name='parent-register'),
    path('print/<str:pref>/<str:sref>/', views.parentPrint, name='parent-print'),
    path('assign/student-to-parent/', views.assignStudent2Parent, name='parent-assign'),
    path('get-parent-student', views.getParentStudent, name='parent-get-parent-student'),
    path('parent/student/<str:sref>/<str:pref>/', views.parentStudent, name='parent-student'),
    path('get/', views.getParent, name='parent-get'),
    path('manage/<str:ref>/', views.manageParent, name='parent-manage'),
    path('disable-parent/<str:ref>/', views.disableParent, name='parent-disable'),
    path('enable-parent/<str:ref>/', views.enableParent, name='parent-enable'),
    path('reset-parent-password/<str:ref>/',views.resetParentPassword,name='parent-reset'),
]