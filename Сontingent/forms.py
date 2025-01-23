from django import forms
from .models import *


class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentDTO
        fields = '__all__'