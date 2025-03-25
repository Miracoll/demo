from django import forms
from .models import News

class NewsForm(forms.ModelForm):
    title = forms.CharField(label='Title',max_length=255,required=True,widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'placeholder':'Title',
        }
    ))
    content = forms.CharField(label='Content',max_length=255,required=True,widget=forms.Textarea(
        attrs={
            'class':'form-control',
            'placeholder':'Content',
            'rows':3,
        }
    ))
    
    class Meta:
        model = News
        fields = ['title','content']