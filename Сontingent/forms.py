from django import forms
from .models import *


class StudentForm(forms.ModelForm):
    COURSE_CHOICES = (
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4)
    )

    course = forms.ChoiceField(choices = COURSE_CHOICES, label='Курс')
    previous_course = forms.ChoiceField(choices = COURSE_CHOICES, label='Курс с которого ушел')

    class Meta:
        model = StudentDTO
        fields = '__all__'