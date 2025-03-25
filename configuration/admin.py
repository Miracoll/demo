from django.contrib import admin
from .models import AllClass,Class,Subject,AllSubject,Role,Session,Term,Category,Config,RegisteredSubjects

# Register your models here.

admin.site.register(AllClass)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(AllSubject)
admin.site.register(Role)
admin.site.register(Session)
admin.site.register(Term)
admin.site.register(Category)
admin.site.register(Config)
admin.site.register(RegisteredSubjects)