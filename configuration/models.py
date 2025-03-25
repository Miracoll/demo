from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.template.defaultfilters import slugify

# Create your models here.

class Class(models.Model):
    group = models.CharField(max_length=10)
    category = models.CharField(max_length=20, blank=True, null=True)
    level = models.IntegerField(default=1)
    code = models.CharField(max_length=3)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.group

class AllClass(models.Model):
    group = models.CharField(max_length=10)
    arm = models.CharField(max_length=10)
    teacher = models.CharField(max_length=100, null=True, blank=True)
    owner = models.CharField(max_length=100, null=True, blank=True)
    CA_max = models.IntegerField(default=40)
    exam_max = models.IntegerField(default=60)
    number_of_subjects = models.IntegerField(blank=True, null=True)
    number_of_student = models.IntegerField(null=True, blank=True)
    promotion_score = models.IntegerField(blank=True, null=True)
    lock = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    approve_result = models.IntegerField(default=0)
    year = models.CharField(max_length=5, blank=True, null=True)
    term = models.CharField(max_length=5, blank=True, null=True)
    class_teacher_name = models.CharField(max_length=100,blank=True, null=False)
    class_teacher_signature = models.ImageField(max_length=100,blank=True, null=True, upload_to='signature')
    overall_result_approval = models.BooleanField()
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    access = models.CharField(max_length=100)
    category = models.CharField(max_length=10)
    session = models.CharField(max_length=10, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.group}{self.arm}'
    
    class Meta:
        ordering = ['group','arm']

class Subject(models.Model):
    subject = models.CharField(max_length=30)
    category = models.CharField(max_length=20, blank=True, null=True)
    teacher = models.CharField(max_length=15, blank=True, null=True)
    group = models.CharField(max_length=10, blank=True, null=True)
    arm = models.CharField(max_length=10, blank=True, null=True)
    # owner = models.CharField(max_length=7, blank=True, null=True)
    upload = models.IntegerField(default=0)
    lock = models.IntegerField(default=0)
    total_student = models.IntegerField(blank=True, null=True)
    approve_result = models.IntegerField(default=0)
    year = models.CharField(max_length=5, blank=True, null=True)
    term = models.CharField(max_length=5, blank=True, null=True)
    session = models.CharField(max_length=10, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.group}{self.arm} {self.subject}'

class AllSubject(models.Model):
    subject = models.CharField(max_length=30)
    category = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject

class Term(models.Model):
    term = models.IntegerField()
    active = models.IntegerField(default=0)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.term} term'

class Arm(models.Model):
    # group = models.ForeignKey(Class, on_delete=models.CASCADE)
    arm = models.CharField(max_length=10)
    # class_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.arm} term'

class Session(models.Model):
    session = models.CharField(max_length=20)
    year = models.IntegerField()
    active = models.IntegerField(default=0)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.session

    class Meta:
        ordering = ['-session']

class Role(models.Model):
    role = models.CharField(max_length=30)
    keyword = models.SlugField()
    code = models.CharField(max_length=3)
    active = models.IntegerField(default=1)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.keyword = slugify(self.role)
        super(Role, self).save(*args, **kwargs)

    def __str__(self):
        return self.role

class Config(models.Model):
    entry = models.IntegerField(default=1)
    school_name = models.CharField(max_length=100, blank=True, null=True)
    school_address = models.CharField(max_length=100, blank=True, null=True)
    school_initial = models.CharField(max_length=5, blank=True, null=True)
    school_domain_name = models.CharField(max_length=255, blank=True, null=True)
    school_logo = models.ImageField(blank=True, null=True)
    anual_result = models.CharField(max_length=8, blank=True, null=True)
    start_result = models.BooleanField(default=False)
    card_usage = models.IntegerField(default=5)
    student_unique = models.IntegerField(blank=True, null=True)
    staff_unique = models.IntegerField(blank=True, null=True)
    parent_unique = models.IntegerField(blank=True, null=True)
    # result_start = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    use_hostel = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.school_name} CONFIGURATION'

class Category(models.Model):
    category = models.CharField(max_length=10)
    code = models.IntegerField()
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.category

class RegisteredSubjects(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    student = models.CharField(max_length=20)
    subject = models.CharField(max_length=50)
    group = models.CharField(max_length=10)
    arm = models.CharField(max_length=20)
    term = models.CharField(max_length=5, null=True, blank=True)
    session = models.CharField(max_length=20, null=True, blank=True)
    category = models.CharField(max_length=10)
    active = models.BooleanField(default=True)
    lock = models.BooleanField(default=False)
    ref = models.UUIDField(default=uuid.uuid4,editable=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.student