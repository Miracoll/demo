from django.contrib import admin
from .models import Student, Paid_Student

# Register your models here.

admin.site.register(Student)
admin.site.register(Paid_Student)