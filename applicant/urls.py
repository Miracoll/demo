from django.urls import path
from . import views

urlpatterns = [
    path('register/<str:pk>/', views.registerstudent, name='register_student'),
    path('new/applicant/', views.preregstudent, name='pre_register_student'),
    path('continue/application/', views.continuereg, name='continue_reg'),
    # path('guardian/<str:ref>', views.parentInfo, name='applicant-parent'),
    path('print/application/slip/<str:pk>/', views.printregister, name='print'),
    path('application/payment/<str:pk>/', views.printrrr, name='print_rrr'),
    path('applicant/receipt/<str:pk>/', views.applicantreceipt, name='applicantpaid'),
    path('registration/mode/', views.startstopreg, name='startstopreg')
]