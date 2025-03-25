from django import forms
from student.models import Student

class StudentRegForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_name','first_name','other_name','']