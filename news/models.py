from email.policy import default
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
from PIL import Image

# Create your models here.

class News(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField(max_length=150)
    receiver = models.CharField(max_length=100, default='all')
    private = models.BooleanField()
    sms = models.BooleanField(default=False)
    email = models.BooleanField(default=True)
    dashboard = models.BooleanField(default=True)
    reference = models.UUIDField(default=uuid.uuid4,editable=False)
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.title} on {self.created}'

    # def save(self):
    #     super().save()
    #     img = Image.open(self.image.path)
    #     img_output = (1024,768)
    #     img.thumbnail(img_output)
    #     img.save(self.image.path)