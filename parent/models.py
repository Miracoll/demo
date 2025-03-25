from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from PIL import Image

# Create your models here.

class Parent(models.Model):
    title = models.CharField(max_length=10)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    unique_number = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    passport = models.ImageField(upload_to='parent_passport', default='passport.jpg')
    current_student = models.CharField(max_length=50)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.unique_number

    # def save(self,*args,**kwargs):
    #     super(Staff,self).save(*args,**kwargs)

    #     img = Image.open(self.passport.path)
    #     if img.height > 499 or img.width > 498:
    #         output_size = (499,498)
    #         img.thumbnail(output_size)
    #         img.save(self.passport.path)

class ParentStudent(models.Model):
    student = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='registered_student')
    parent = models.ForeignKey(Parent, on_delete=models.DO_NOTHING)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.parent.unique_number

    # def save(self,*args,**kwargs):
    #     super(Staff,self).save(*args,**kwargs)

    #     img = Image.open(self.passport.path)
    #     if img.height > 499 or img.width > 498:
    #         output_size = (499,498)
    #         img.thumbnail(output_size)
    #         img.save(self.passport.path)