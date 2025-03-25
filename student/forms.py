from django import forms
from student.models import Student
from lms.models import Profile

class StudentImage(forms.ModelForm):
    address = forms.CharField(label='Address',required=True,widget=forms.Textarea(
        attrs={
            'placeholder':'Address...',
            'rows':2,
        }
    ))
    dob = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(
            format='%Y-%m-%d', 
            attrs={
                'placeholder': 'YYYY-MM-DD', 
                'type': 'date',
            }
        )
    )
    class Meta:
        model = Student
        fields = ['last_name','first_name','other_name','email','dob','mobile','address','passport']

class ProfileImage(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['passport']