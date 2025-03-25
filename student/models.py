from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image

# Create your models here.

class Paid_Student(models.Model):
    student = models.CharField(max_length=255)
    amount_paid = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    term = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    group = models.CharField(max_length=15, blank=True, null=True)
    arm = models.CharField(max_length=10, blank=True, null=True)
    status = models.IntegerField(default=1)
    installment = models.IntegerField(blank=True, null=True)
    print = models.IntegerField(default=1)
    complete = models.BooleanField(default=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    paid_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.student} tuition fee'

    class Meta:
        ordering = ['-created_on']
    
class Student(models.Model):
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    other_name = models.CharField(max_length=20, null=False, blank=True)
    sex = models.CharField(max_length=20,blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    token = models.CharField(max_length=20, blank=True, null=True)
    birth_day = models.CharField(max_length=2, blank=True, null=True)
    birth_month = models.CharField(max_length=2, blank=True, null=True)
    birth_year = models.CharField(max_length=4, blank=True, null=True)
    address = models.TextField(max_length=150)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    level = models.IntegerField(default=0)
    group = models.CharField(max_length=5,blank=True, null=True)
    arm = models.CharField(max_length=15,blank=True, null=True)
    active = models.IntegerField(default=1)
    passport = models.ImageField(upload_to='passport', default='passport.jpg')
    registration_number = models.CharField(max_length=255,blank=True, null=True)
    category = models.CharField(max_length=10)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    relationship = models.CharField(max_length=10,blank=True, null=True)
    full_name = models.CharField(max_length=100,blank=True, null=True)
    nok_address = models.TextField(max_length=150,blank=True, null=True)
    nok_mobile = models.CharField(max_length=15,blank=True, null=True)
    nok_email = models.EmailField(blank=True, null=True)
    guardian_title = models.CharField(max_length=10)
    guardian_last_name = models.CharField(max_length=20)
    guardian_first_name = models.CharField(max_length=20)
    guardian_mobile = models.CharField(max_length=15)
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_address = models.TextField(max_length=150)
    lock = models.IntegerField(default=0)
    graduated = models.BooleanField(default=False)
    register_course = models.BooleanField(default=False)
    term = models.CharField(max_length=5, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    session = models.CharField(max_length=10, blank=True, null=True)
    applicant_number = models.CharField(max_length=20, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.registration_number
    
    class Meta:
        ordering = ['registration_number']

    # def save(self,*args,**kwargs):
    #     super(Student,self).save(*args,**kwargs)

    #     img = Image.open(self.passport.path)
    #     if img.height > 499 or img.width > 498:
    #         output_size = (499,498)
    #         img.thumbnail(output_size)
    #         img.save(self.passport.path)