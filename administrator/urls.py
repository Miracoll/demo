from django.urls import path
from . import views

urlpatterns = [
    path('superadmin/', views.superadmin, name='superadmin'),
]