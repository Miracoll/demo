from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.

class Record(models.Model):
    CA1 = models.DecimalField(default=0.0, blank=True, null=True,max_digits=5,decimal_places=2)
    CA2 = models.DecimalField(default=0.0, blank=True, null=True,max_digits=5,decimal_places=2)
    CA3 = models.DecimalField(default=0.0, blank=True, null=True,max_digits=5,decimal_places=2)
    project = models.DecimalField(default=0.0, blank=True, null=True,max_digits=5,decimal_places=2)
    test = models.DecimalField(default=0.0, blank=True, null=True,max_digits=5,decimal_places=2)
    exam = models.DecimalField(default=0.0, blank=True, null=True,max_digits=5,decimal_places=2)
    total = models.DecimalField(default=0.0, blank=True, null=True,max_digits=9,decimal_places=2)
    average = models.DecimalField(default=0, blank=True, null=True,max_digits=9,decimal_places=2)
    annaul_average = models.DecimalField(default=0.0, blank=True, null=True,max_digits=9,decimal_places=2)
    # annaul_total = models.DecimalField(default=0, blank=True, null=True,max_digits=9,decimal_places=2)
    grade = models.CharField(max_length=15, blank=True, null=True)
    remark = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=5, blank=True, null=True)
    group = models.CharField(max_length=10)
    arm = models.CharField(max_length=10)
    subject = models.CharField(max_length=100)
    term = models.IntegerField()
    student = models.CharField(max_length=255)
    lock = models.IntegerField(default=0, blank=True, null=True)
    active = models.BooleanField(default=False)
    session = models.CharField(max_length=10, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Record_Deleted(models.Model):
    CA1 = models.IntegerField(default=0, blank=True, null=True)
    CA2 = models.IntegerField(default=0, blank=True, null=True)
    CA3 = models.IntegerField(default=0, blank=True, null=True)
    project = models.IntegerField(default=0, blank=True, null=True)
    test = models.IntegerField(default=0, blank=True, null=True)
    exam = models.IntegerField(default=0, blank=True, null=True)
    total = models.IntegerField(default=0, blank=True, null=True)
    average = models.IntegerField(default=0, blank=True, null=True)
    grade = models.CharField(max_length=15, blank=True, null=True)
    remark = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=3, blank=True, null=True)
    group = models.CharField(max_length=5)
    arm = models.CharField(max_length=5)
    subject = models.CharField(max_length=20)
    term = models.IntegerField()
    student = models.CharField(max_length=255)
    lock = models.IntegerField(default=0, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    active = models.IntegerField(default=1, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Grade(models.Model):
    min_score = models.FloatField()
    max_score = models.FloatField()
    grade = models.CharField(max_length=5)
    remark = models.CharField(max_length=20)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.grade