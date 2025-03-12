from django import forms
from Academhub.base.forms import *

from Academhub.models import Student, Discipline, GroupStudents, Specialty, Qualification

__all__ = [
    'DisciplineForm', 
    'StudentForm',
    'GroupForm',
    'QualificationForm',
    'SpecialtyForm',
]

class DisciplineForm(forms.ModelForm):
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        label='Специальность',
    )

    class Meta:
        model = Discipline
        fields = [
            'name',
            'code',
            'specialty',
        ]

class StudentForm(forms.ModelForm):
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов Иван Иванович'
            }
        )
    )

    representative_full_name = forms.CharField(
        label='ФИО представителя',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов Иван Иванович'
            }
        )
    )

    phone = forms.CharField(
        label='Телефон',
        widget=Phone(attrs={'class': 'phone-input'})
    )

    snils = forms.CharField(
        label='Снилс',
        max_length=14,
        widget=Snils(attrs={
            'class': 'delete-arrow-input-number'
        })
    )

    representative_email = forms.EmailField(
        label='Почта представителя',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'email@email.email'
            }
        )
    )

    class Meta:
        model = Student
        fields = [
            'full_name',
            'phone',
            'birth_date',
            'snils',
            'admission_order',
            'education_base',
            'education_basis',
            'group',
            'registration_address',
            'actual_address',
            'representative_full_name',
            'representative_email',
            'note',
        ] 

class GroupForm(forms.ModelForm):
    # disciplines = forms.ModelMultipleChoiceField(
    #     queryset=Discipline.objects.all(),
    #     label='Дисциплины',
    #     widget=forms.CheckboxSelectMultiple()
    # )

    class Meta:
        model = GroupStudents
        fields = [
            'qualification',
            'year_create',
            'education_base',
            'current_course',
            # 'disciplines',
        ]

class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = '__all__'

class SpecialtyForm(forms.ModelForm ):
    class Meta:
        model = Specialty
        fields = '__all__'

class AcademLeaveForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            'academ_leave_date',
            'academ_return_date',
            'reason_of_academ',
            'academ_order'
        ]
        widgets = {
            'academ_leave_date': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            ),
            'academ_return_date': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            ),
        }

    def save(self, commit=True):
        student = super().save(commit=False)  # Получаем объект студента, но пока не сохраняем
        student.is_in_academ = True  # Переводим в академ
        student.expelled_due_to_graduation = False
        student.left_course = student.group.current_course  # Берем текущий курс группы

        if commit:
            student.save()  # Сохраняем изменения
        return student

class AcademReturnForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = []

    def save(self, commit=True):
        student = super().save(commit=False)  # Получаем объект студента, но пока не сохраняем
        student.is_in_academ = False
        student.academ_leave_date = None
        student.academ_return_date = None
        student.reason_of_academ = None
        student.left_course = None
        student.expelled_due_to_graduation = False
        student.academ_order = ""
        student.save()

        if commit:
            student.save()  # Сохраняем изменения
        return student

class ExpellStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'date_of_expelling',
            'reason_of_expelling',
            'expell_order',
        ]

        widgets = {
            'date_of_expelling': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            )
        }

    def save(self, commit=True):
        student = super().save(commit=False)  # Получаем объект студента, но пока не сохраняем
        student.is_expelled = True
        student.left_course = student.group.current_course  # Берем текущий курс группы
        student.academ_leave_date = None
        student.academ_return_date = None
        student.reason_of_academ = None
        student.is_in_academ = False
        student.expelled_due_to_graduation = False
        if commit:
            student.save()  # Сохраняем изменения
        return student

class RecoverStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['group',
                  'reinstaitment_order']

    def save(self, commit=True):
        student = super().save(commit=False)
        student.is_expelled = False
        student.date_of_expelling = None
        student.reason_of_expelling = None
        student.left_course = None
        student.expelled_due_to_graduation = False
        if commit:
            student.save()
        return student
