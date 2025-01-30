from django import forms

from Academhub.models import Student
from .models import *


class StudentForm(forms.ModelForm):
    birth_date = forms.DateField(
        input_formats='%d.%m.%Y',
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

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
