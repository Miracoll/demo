from django.urls import path
from . import views

urlpatterns = [
    path('', views.news, name='news'),
    path('create/news/', views.createnews, name='createnews'),
    path('create/private-news/', views.private_news, name='privatenews'),
]