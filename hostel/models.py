from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Hostel(models.Model):
    hostel_name = models.CharField(max_length=255)
    floor_number = models.IntegerField()
    image = models.ImageField(upload_to='hostel', default='hostel.jpg')
    # amount = models.IntegerField()
    active = models.BooleanField(default=True)
    lock = models.BooleanField(default=False)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Floor(models.Model):
    floor = models.CharField(max_length=10)
    number_of_room = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    hostel_id = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    lock = models.BooleanField(default=False)
    last_updated_by = models.CharField(max_length=255, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.floor} of {self.hostel_id.hostel_name}'

    class Meta:
        ordering = ['hostel_id','created']

class Room(models.Model):
    room = models.CharField(max_length=50)
    occupant_per_room = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    occupied = models.IntegerField(default=0)
    space_available = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    lock = models.BooleanField(default=False)
    last_updated_by = models.CharField(max_length=255, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Bedspace(models.Model):
    bedspace = models.CharField(max_length=255)
    occupied = models.IntegerField(default=0)
    active = models.BooleanField(default=True)  #If bedspace is allowed
    lock = models.BooleanField(default=False)   #for occupant status
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Occupant(models.Model):
    student = models.CharField(max_length=255)
    amount_paid = models.CharField(max_length=100)
    bedspace = models.ForeignKey(Bedspace, on_delete=models.CASCADE)
    year = models.CharField(max_length=10)
    session = models.CharField(max_length=100)
    term = models.CharField(max_length=5)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Paid_Occupant(models.Model):
    occupant = models.CharField(max_length=255)
    amount_paid = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    ref = models.CharField(max_length=200)
    term = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    group = models.CharField(max_length=5, blank=True, null=True)
    arm = models.CharField(max_length=5, blank=True, null=True)
    status = models.IntegerField(default=1)
    installment = models.IntegerField(blank=True, null=True)
    hostel = models.CharField(max_length=255)
    print = models.IntegerField(default=1)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    paid_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.occupant} hostel fee'

    class Meta:
        ordering = ['-created_on']