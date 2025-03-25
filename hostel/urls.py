from django.urls import path
from . import views

urlpatterns = [
    path('', views.createhostel, name='createhostel'),
    path('unavailable-service/',views.nohostel,name='no_hostel'),
    path('payment/',views.payment_setup,name='paymentsetup'),
    path('floor/', views.hostelfloor, name='hostelfloor'),
    path('room/', views.hostelroom, name='hostelroom'),
    path('bedspace/', views.hostelbedspace, name='hostelbedspace'),
    path('assign/', views.assignhostel, name='assignhostel'),
    path('view/<str:pk>/assign/', views.viewhostel, name='viewhostel'),
    path('assign/occupant/<str:pk>/<str:regg>/', views.assign2occupant, name='assign2occupant'),
    path('printout/<str:pk>/', views.hostelprintout, name='hostelprintout'),
]