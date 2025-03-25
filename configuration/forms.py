from django import forms
# from django.contrib.auth.models import User
from .models import Config

class ConfigUpdateForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = ['school_name','school_initial','school_address','school_domain_name','school_logo','card_usage','staff_unique','student_unique','parent_unique','use_hostel']