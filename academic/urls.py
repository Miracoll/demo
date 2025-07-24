from django.urls import path
from . import views

urlpatterns = [
    path('assessment/', views.assessment, name='assessment'),
    path('admin-assessment/', views.admin_assessment, name='admin_assessment'),
    path('eassessment/',views.eassessment, name='eassessment'),
    path('class/setup/',views.class_academics, name='class_academics'),
    path('activate-result/',views.computation_error, name='computation_error'),
    path('computation/',views.computation, name='computation'),
]