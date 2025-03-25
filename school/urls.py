"""school URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('manager/', admin.site.urls),
    path('',include('frontpage.urls')),
    path('portal/',include('studentpage.urls')),
    path('admin/', include('lms.urls')),
    path('admin/configuration/', include('configuration.urls')),
    path('admin/staff/', include('staff.urls')),
    path('admin/student/', include('student.urls')),
    path('admin/news/', include('news.urls')),
    path('admin/activity/', include('activity.urls')),
    path('admin/result/', include('result.urls')),
    path('admin/card/', include('card.urls')),
    path('admin/payment/', include('payment.urls')),
    path('admin/attendance/', include('attendance.urls')),
    path('admin/messaging/', include('messaging.urls')),
    path('admin/academic/', include('academic.urls')),
    path('admin/administrator/', include('administrator.urls')),
    path('admin/hostel/', include('hostel.urls')),
    path('admin/applicant/', include('applicant.urls')),
    path('admin/parent/', include('parent.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)