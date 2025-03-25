from django.contrib import admin
from .models import Applicant,Paid_Applicant

# Register your models here.

admin.site.register(Applicant)
admin.site.register(Paid_Applicant)