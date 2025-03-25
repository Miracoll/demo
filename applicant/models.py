from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Applicant(models.Model):
    applicant_number = models.CharField(max_length=10, null=True, blank=True)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    other_name = models.CharField(max_length=20)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    group = models.CharField(max_length=5, default='JS1')
    arm = models.CharField(max_length=10)
    term = models.CharField(max_length=5, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    category = models.CharField(max_length=10)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    paid_on = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    sex = models.CharField(max_length=20,blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    birth_day = models.CharField(max_length=2, blank=True, null=True)
    birth_month = models.CharField(max_length=2, blank=True, null=True)
    birth_year = models.CharField(max_length=4, blank=True, null=True)
    address = models.TextField(max_length=150, blank=True, null=True)
    level = models.IntegerField(default=0, blank=True, null=True)
    group = models.CharField(max_length=5,blank=True, null=True)
    arm = models.CharField(max_length=15,blank=True, null=True)
    active = models.IntegerField(default=1, blank=True, null=True)
    passport = models.ImageField(upload_to='passport', default='passport.jpg', blank=True, null=True)
    registration_number = models.CharField(max_length=255,blank=True, null=True)
    relationship = models.CharField(max_length=10,blank=True, null=True)
    full_name = models.CharField(max_length=100,blank=True, null=True)
    nok_address = models.TextField(max_length=150,blank=True, null=True)
    nok_mobile = models.CharField(max_length=15,blank=True, null=True)
    nok_email = models.EmailField(blank=True, null=True)
    guardian_title = models.CharField(max_length=10, blank=True, null=True)
    guardian_last_name = models.CharField(max_length=20, blank=True, null=True)
    guardian_first_name = models.CharField(max_length=20, blank=True, null=True)
    guardian_mobile = models.CharField(max_length=15, blank=True, null=True)
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_address = models.TextField(max_length=150, blank=True, null=True)
    registered = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.applicant_number

class Paid_Applicant(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.DO_NOTHING)
    email = models.EmailField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    payment_ref = models.CharField(max_length=200, blank=True, null=True)
    status = models.IntegerField(default=0)
    term = models.CharField(max_length=5, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    date_paid = models.DateTimeField(auto_now=True)
    cleared_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    # approved_by = models.CharField(max_length=10, blank=True, null=True)
    manual_cleared = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.email} payment'