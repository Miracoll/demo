from django.db import models
from django.utils import timezone
import uuid

# Create your models here.

class Card(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    pin = models.CharField(max_length=20)
    serial = models.CharField(max_length=20)
    usage = models.IntegerField(default=0)
    student = models.CharField(max_length=255, blank=True, null=True)
    group = models.CharField(max_length=15, blank=True, null=True)
    arm = models.CharField(max_length=10, blank=True, null=True)
    term = models.CharField(max_length=5, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    created = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)