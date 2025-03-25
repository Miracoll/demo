from django import forms
from .models import Parent

class ParentUpadateForm(forms.ModelForm):
    class Meta:
        model=Parent
        fields = ['last_name','first_name','mobile','address','email']