from django import forms

from Academhub.models import Student
from .models import *


class StudentForm(forms.ModelForm):
    COURSE_CHOICES = (
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4)
    )

    course = forms.ChoiceField(choices = COURSE_CHOICES, label='Курс')
    # previous_course = forms.ChoiceField(choices = COURSE_CHOICES, label='Курс с которого ушел')

    class Meta:
        model = Student
        fields = [
            'full_name',
            'phone',
            'birth_date',
            'course',
            'group',
            'admission_order',
            'education_base',
            'education_basis',
            'registration_address',
            'actual_address',
            'representative_full_name',
            'representative_email',
            'note',
        ]  # Указываем только нужные поля
