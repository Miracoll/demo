from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Result(models.Model):
    student = models.CharField(max_length=255)
    total = models.DecimalField(default=0.0, blank=True, null=True, max_digits=9, decimal_places=2)
    average = models.DecimalField(default=0.0, blank=True, null=True, max_digits=9, decimal_places=2)
    position = models.CharField(max_length=5, blank=True, null=True)
    present = models.IntegerField(blank=True, null=True)
    absent = models.IntegerField(blank=True, null=True)
    total_days = models.IntegerField(blank=True, null=True)
    term = models.IntegerField()
    group = models.CharField(max_length=10)
    arm = models.CharField(max_length=10)
    remark = models.CharField(max_length=15)
    year = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    principalcomment = models.TextField(max_length=200, blank=True, null=True)
    gccomment = models.TextField(max_length=200, blank=True, null=True)
    hostelcomment = models.TextField(max_length=200, blank=True, null=True)
    teachercomment = models.TextField(max_length=200, blank=True, null=True)
    approve = models.IntegerField(default=0, blank=True, null=True)
    active = models.BooleanField(default=False)
    attentiveness = models.IntegerField(blank=True, null=True)
    politeness = models.IntegerField(blank=True, null=True)
    neatness = models.IntegerField(blank=True, null=True)
    moral_concepts = models.IntegerField(blank=True, null=True)
    punctuality = models.IntegerField(blank=True, null=True)
    social_attitudes = models.IntegerField(blank=True, null=True)
    hand_writing = models.IntegerField(blank=True, null=True)
    speech_fluency = models.IntegerField(blank=True, null=True)
    lab = models.IntegerField(blank=True, null=True)
    sport = models.IntegerField(blank=True, null=True)
    communication = models.IntegerField(blank=True, null=True)
    thinking = models.IntegerField(blank=True, null=True)
    qrcode = models.ImageField(blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.student

class Comment(models.Model):
    comment = models.TextField(max_length=200)
    score = models.IntegerField(null=True, blank=True)
    owner = models.CharField(max_length=20, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.comment