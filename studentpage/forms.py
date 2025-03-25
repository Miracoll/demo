from django import forms
# from django.contrib.auth.models import User
from student.models import Student
from lms.models import Profile

class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['registration_number','first_name','last_name','other_name','sex','address','mobile','dob','email']