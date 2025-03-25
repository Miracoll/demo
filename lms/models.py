from django.db import models
from configuration.models import Role
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,blank=True,null=True)
    passport = models.ImageField(upload_to='passport', default='passport.jpg')
    blocked_reason = models.CharField(max_length=100, null=True, blank=True)
    set_password = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.user.username} profile'

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    created = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name