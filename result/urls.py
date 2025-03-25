from django.urls import path
from . import views

urlpatterns = [
    path('template/', views.resulttemplate, name='result_template'),
    # path('datasheet/', views.resultDatasheet, name='result_datasheet'),
    path('broadsheet/', views.broadsheet, name='broadsheet'),
    path('personality/', views.personality, name='personality'),
    path('term/result/', views.termresult, name='term_result'),
    path('check/<str:pk>/', views.displayresult, name='display_result'),
    path('student/result/<str:pk>/', views.displayresultpdf, name='display_result_pdf'),
    path('comment/', views.resultcomment, name='result_comment'),
    path('approve/', views.approveresult, name='result_approve'),
    path('compute/', views.resultcomputation, name='result_compute'),
    # path('start/', views.startresult, name='start_result'),
    path('status/', views.resultstatus, name='result_status'),
    path('upload/', views.getupload, name='get_upload'),
    path('manage/upload/result/<str:pk>', views.manageupload, name='manage_upload'),
    path('manage/upload/<str:pk>/', views.unlockresultupload, name='unlock_result'),
    path('approve/class/result/',views.approveclassresult, name='approve_class_result'),
    path('approve/<str:pk>/', views.approveresultclick, name='approve'),
    path('take-subject', views.allocateSubject, name='allocate'),
]