from django.urls import path
from . import views

urlpatterns = [
    path('register-staff/', views.registerstaff, name='register_teacher'),
    path('disable-staff/', views.disablestaff, name='disable_staff'),
    path('enable-staff/', views.enablestaff, name='enable_staff'),
    path('manage-staff/entry/', views.getstaff, name='get_staff'),
    path('manage-staff/<str:pk>/', views.managestaff, name='manage_staff'),
    path('edit-staff-reg/', views.editstaffreg, name='edit_staff_reg'),
    path('printout/<str:reference>', views.printstaff, name='printstaff'),
    path('reset-staff-password/',views.resetstaffpassword,name='staffpasswordreset'),
]