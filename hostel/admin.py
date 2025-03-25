from django.contrib import admin
from .models import Hostel,Floor,Room,Bedspace,Occupant,Paid_Occupant

# Register your models here.

admin.site.register(Hostel)
admin.site.register(Floor)
admin.site.register(Room)
admin.site.register(Bedspace)
admin.site.register(Occupant)
admin.site.register(Paid_Occupant)