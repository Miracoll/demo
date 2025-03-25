from django.urls import path
from . import views

urlpatterns = [
    path('',views.Home.as_view(),name='frontpage'),
    path('about/',views.About.as_view(),name='frontpage-about'),
    path('contact/',views.Contact.as_view(),name='frontpage-contact'),
    path('admission/',views.Admission.as_view(),name='frontpage-admission'),
    path('newsletter/',views.Newsletter.as_view(),name='frontpage-newsletter'),
]