from django.contrib import admin
from .models import Record,Record_Deleted,Grade

# Register your models here.

admin.site.register(Record)
admin.site.register(Record_Deleted)
admin.site.register(Grade)