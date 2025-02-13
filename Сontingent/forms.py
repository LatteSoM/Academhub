from django import forms
from Academhub.base import widgets

from Academhub.models import Student, Discipline, GroupStudents, Specialty, Gradebook, Qualification, CustomUser


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
        widget=widgets.Phone(attrs={
            'placeholder': '+7 (XXX) XXX-XX-XX',
            'class': 'delete-arrow-input-number'
        }),
    )

    snils = forms.CharField(
        label='Снилс',
        max_length=14,
        widget=widgets.Snils(attrs={
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

class GradebookForm(forms.ModelForm):
    """
    Форма для создания и редактирования записей в журнале оценок.
    """
    teacher = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_teacher=True),
        label='Преподаватель',
    )
    discipline = forms.ModelChoiceField(
        queryset=Discipline.objects.all(),
        label='Дисциплина',
    )
    groups = forms.ModelChoiceField(
        queryset=GroupStudents.objects.all(),
        label='Группа'
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        label='Студенты',
    )

    group_id = None

    class Meta:
        """
        Метакласс для настройки формы.
        """
        model = Gradebook
        fields = ['name', 'teacher', 'discipline', 'groups', 'students']

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.
        """
        properties = kwargs.pop('properties', None)
        if properties:
            self.group_id = properties['group_id']

        super().__init__(*args, **kwargs)

        if self.group_id:
            self.initial['groups'] = self.group_id

        self.fields['students'].queryset = self.get_student_queryset()

    def get_group_queryset(self):
        """
        Возвращает queryset для группы.

        Returns:
            QuerySet: QuerySet для группы.
        """
        try:
            return GroupStudents.objects.filter(pk=self.group_id)
        except:
            return GroupStudents.objects.all()

    def get_student_queryset(self):
        """
        Возвращает queryset для студентов.

        Returns:
            QuerySet: QuerySet для студентов.
        """
        try:
            return Student.objects.filter(group__id=self.group_id)
        except:
            return Student.objects.none()
