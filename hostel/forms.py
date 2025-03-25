from dataclasses import field
from django import forms
from .models import Hostel

class HostelForm(forms.ModelForm):
    hostel_name = forms.CharField(label='Hostel name',max_length=30,required=True,widget=forms.TextInput(
        attrs={
            'class':'form-control text-capitalize',
            'placeholder':'Unique hostel name',
        }
    ))
    floor_number = forms.IntegerField(label='Number of hostel floor',required=True,widget=forms.NumberInput(
        attrs={
            'class':'form-control',
            'placeholder':'Number of hostel floor',
        }
    ))
    image = forms.ImageField(label='Upload hostel picture')
    class Meta:
        model = Hostel
        fields = ['hostel_name', 'floor_number', 'image']