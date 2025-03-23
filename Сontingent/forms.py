import os
from .utils import *
from django import forms
from datetime import datetime
from Academhub.forms import *
from django.utils.dateparse import parse_date
from openpyxl.reader.excel import load_workbook
from django.core.exceptions import ValidationError
from Academhub.models import Student, Discipline, GroupStudents, Specialty, Qualification

__all__ = [
    'GroupForm',
    'StudentForm',
    'SpecialtyForm',
    'DisciplineForm', 
    'StudentImportForm',
    'QualificationForm',
    'PromoteGroupStudentsForm',
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
        model = CurrentStudent
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
    class Meta:
        model = GroupStudents
        fields = [
            'qualification',
            'year_create',
            'education_base',
            'current_course',
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
        model = CurrentStudent
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
        fields = [
            'group',
            'reinstaitment_order'
        ]

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


class StudentImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Выберите файл Excel (.xlsx)"
    )


    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data['excel_file']

        if file:
            file_extension = os.path.splitext(file.discipline_name)[1]

            if file_extension.lower() != '.xlsx':
                raise ValidationError("Файл должен быть в формате .xlsx")
        
            self.get_data_from_file(file)

        return file
    
    def get_data_from_file(self, file):
        wb = load_workbook(file)
        ws = wb.active

        headers = {
            cell.value: idx for idx, cell in enumerate(ws[1]) if cell.value
        }

        for row in ws.iter_rows(min_row=2, values_only=True):
            last_name = row[headers.get("Фамилия")]
            first_name = row[headers.get("Имя")]
            middle_name = row[headers.get("Отчество")]
            self.full_name = f"{last_name} {first_name} {middle_name}".strip() if last_name and first_name else None
            group_number = row[headers.get("Академическая группа")]
            course_str = row[headers.get("Курс")]
            self.course = int(course_str[0]) if course_str and course_str[0].isdigit() else None
            self.education_basis = row[headers.get("Основы обучения")]
            self.birth_date = (
                row[headers.get("Дата рождения")].date() if isinstance(row[headers.get("Дата рождения")],datetime)
                else datetime.strptime(row[headers.get("Дата рождения")], "%d.%m.%Y").date()) if row[
                headers.get("Дата рождения")] else None

            self.phone = row[headers.get("Телефон мобильный")]
            self.admission_order = row[headers.get("Приказ о зачислении")]
            self.expell_order = row[headers.get("Приказ об отчислении")] if row[
                headers.get("Приказ об отчислении")] else None
            self.date_of_expelling = (
                row[headers.get("Приказ об отчислении дата ОТ")].date() if isinstance(row[headers.get("Приказ об отчислении дата ОТ")], datetime)
                else datetime.strptime(row[headers.get("Приказ об отчислении дата ОТ")], "%d.%m.%Y").date()) if row[
                headers.get("Приказ об отчислении дата ОТ")] else None
            self.academ_leave_date = parse_date(str(row[headers.get("Дата начала последнего академ отпуска")])) if \
            row[headers.get("Дата начала последнего академ отпуска")] else None
            self.academ_return_date = parse_date(
                str(row[headers.get("Дата окончания последнего академ отпуска")])) if row[
                headers.get("Дата окончания последнего академ отпуска")] else None
            self.registration_addres = row[headers.get("Адрес по прописке")] if row[headers.get("Адрес по прописке")] else None
            self.actual_addres = row[headers.get("Адрес проживания")] if row[headers.get("Адрес проживания")] else None
            self.snils = row[headers.get("СПС")] if row[headers.get("СПС")] else None
            self.ancete_number = extract_application_number(row[headers.get("Анкета абитуриента")])
            self.expelled_due_to_graduation = False
            self.is_expelled = False
            self.reason_of_expelling = None
            self.note = None

            if self.expell_order:
                self.is_expelled = True
                if 'окончании' in self.expell_order:
                    self.expelled_due_to_graduation = True
                    self.reason_of_expelling = "Окончание обучения"
                    self.note = 'Отчислен в связи с окончанием обучения'

            # Проверяем группу
            group_filter = GroupStudents.objects.filter(
                full_name=group_number
            )

            if group_filter.exists():
                self.group = group_filter.first()
            else:
                raise ValidationError(
                    f'Группы {group_number} не существует'
                )

    def save(self):
        # Создаём или обновляем студента
        student, created = Student.objects.update_or_create(
            full_name=self.full_name,
            defaults={
                'birth_date': self.birth_date,
                'group': self.group,
                'education_basis': self.education_basis,
                'phone': self.phone,
                'admission_order': self.admission_order,
                'expell_order': self.expell_order,
                'date_of_expelling': self.date_of_expelling,
                'is_in_academ': bool(self.academ_leave_date and not self.academ_return_date),
                'academ_leave_date': self.academ_leave_date,
                'academ_return_date': self.academ_return_date,
                'registration_address': self.registration_addres,
                'actual_address': self.actual_addres,
                'snils': self.snils,
                'expelled_due_to_graduation': self.expelled_due_to_graduation,
                'reason_of_expelling': self.reason_of_expelling,
                'is_expelled': self.is_expelled,
                'note': self.note,
                'ancete_number': self.ancete_number,
            }
        )