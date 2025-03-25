from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.setup, name='payment_setup'),
    path('application/clear/', views.clearapplication, name='clear_application'),
    path('manage/', views.managepayment, name='manage_payment'),
    path('modify/<str:pk>/', views.modifypayment, name='modify_payment'),
    path('status/get/', views.paidstudent, name='paidstudent'),
    path('tuition/clear', views.cleartuition, name='cleartuition'),
]