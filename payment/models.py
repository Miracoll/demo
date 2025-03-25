from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Payment(models.Model):
    payment = models.CharField(max_length=30)
    amount = models.IntegerField()
    category = models.CharField(max_length=100)
    group = models.CharField(max_length=10)
    # arm = models.CharField(max_length=10)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.payment} --> {self.group}'