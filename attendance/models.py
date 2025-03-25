from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Attendance(models.Model):
    date = models.DateField()
    student = models.CharField(max_length=255)
    status = models.BooleanField()
    teacher = models.CharField(max_length=10)
    lock = models.IntegerField(default=0)
    group = models.CharField(max_length=10, blank=True, null=True)
    arm = models.CharField(max_length=10, blank=True, null=True)
    term = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.student} on {self.date}'