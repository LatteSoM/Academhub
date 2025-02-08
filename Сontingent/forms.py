from django import forms

from Academhub.models import Student, GroupStudents, Specialty, Qualification


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
        max_length=20,
        widget=forms.NumberInput(attrs={
            'placeholder': '+7 (XXX) XXX-XX-XX',
            'class': 'delete-arrow-input-number'
        }),
    )

    snils = forms.CharField(
        label='Снилс',
        max_length=14,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'XXX-XXX-XXX XX',
                'class': 'delete-arrow-input-number'
            }
        ),
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
            'course',
            'snils',
            'group',
            'admission_order',
            'education_base',
            'education_basis',
            'registration_address',
            'actual_address',
            'representative_full_name',
            'representative_email',
            'note',
        ] 

class GroupForm(forms.ModelForm):
    class Meta:
        model = GroupStudents
        fields = '__all__'

class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = '__all__'

class SpecialtyForm(forms.ModelForm ):
    class Meta:
        model = Specialty
        fields = '__all__'
