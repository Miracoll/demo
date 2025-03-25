from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from PIL import Image

# Create your models here.

class Staff(models.Model):
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    other_name = models.CharField(max_length=20, blank=True, null=True)
    sex = models.CharField(max_length=20)
    dob = models.DateField()
    birth_day = models.CharField(max_length=2, blank=True, null=True)
    birth_month = models.CharField(max_length=2, blank=True, null=True)
    birth_year = models.CharField(max_length=4, blank=True, null=True)
    # subject = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    registration_number = models.CharField(max_length=255)
    active = models.IntegerField(default=1)
    passport = models.ImageField(upload_to='teacher_passport', default='passport.jpg')
    complete_registration = models.BooleanField(default=False)
    nok_title = models.CharField(max_length=10)
    nok_relationship = models.CharField(max_length=10)
    nok_full_name = models.CharField(max_length=100)
    nok_address = models.CharField(max_length=150)
    nok_mobile = models.CharField(max_length=15)
    nok_email = models.EmailField(blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instangram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.registration_number

    # def save(self,*args,**kwargs):
    #     super(Staff,self).save(*args,**kwargs)

    #     img = Image.open(self.passport.path)
    #     if img.height > 499 or img.width > 498:
    #         output_size = (499,498)
    #         img.thumbnail(output_size)
    #         img.save(self.passport.path)