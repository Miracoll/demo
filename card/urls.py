from django.urls import path
from . import views

urlpatterns = [
    path('generate-card/', views.generatecard, name='generatecard'),
]