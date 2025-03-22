from django import forms
from Academhub.models import Gradebook, GradebookStudents, CustomUser, Discipline, Student, GroupStudents

__all__ = (
    'GradebookForm',
    'GradebookStudentsForm',
)

class GenerateGradebookForm(forms.Form):

    SEMESTER_NUMBERS = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
    )

    semester = forms.ChoiceField(
        choices=SEMESTER_NUMBERS,
        label="Выберите семестр"
    )


class GetStatisticksGradebookForm(forms.Form):

    SEMESTER_NUMBERS = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
    )

    semester = forms.ChoiceField(
        choices=SEMESTER_NUMBERS,
        label="Выберите семестр"
    )

    group = forms.ModelChoiceField(
        queryset=GroupStudents.objects.all(),
        label="Группы"
    )

class GradebookForm(forms.ModelForm):
    teachers = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(is_teacher=True),
        label='Преподаватели',
        widget=forms.CheckboxSelectMultiple
    )
    discipline = forms.ModelChoiceField(
        queryset=Discipline.objects.none(),
        label='Дисциплина',
    )
    group = forms.ModelChoiceField(
        queryset=GroupStudents.objects.all(),
        label='Группа'
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        label='Студенты',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Gradebook
        fields = ['name', 'semester_number', 'type_of_grade_book',
                  'amount_of_days_for_closing', 'teachers', 'group',
                  'discipline', 'students']

    def __init__(self, *args, **kwargs):
        properties = kwargs.pop('properties', {})
        super().__init__(*args, **kwargs)

        # Для существующих объектов
        if self.instance.pk:
            self._configure_existing_instance(properties)
        # Для новых объектов
        else:
            self._configure_new_instance(properties)

    def _configure_existing_instance(self, properties):
        """Настройка для редактирования существующей ведомости"""
        self.group_id = self.instance.group.pk

        # Получаем текущих студентов ведомости
        current_students_ids = self.instance.students.values_list('id', flat=True)

        # Устанавливаем начальные значения
        self.initial.update({
            'group': self.group_id,
            'discipline': self.instance.discipline.pk,
            'students': list(current_students_ids),
            'teachers': list(self.instance.teachers.values_list('pk', flat=True))
        })

        # Настраиваем queryset для студентов
        self.fields['students'].queryset = Student.objects.filter(
            group__id=self.group_id
        )

        # Настраиваем дисциплины для группы
        specialty = self.instance.group.qualification.specialty
        self.fields['discipline'].queryset = specialty.disciplines.all()

    def _configure_new_instance(self, properties):
        """Настройка для создания новой ведомости"""
        self.group_id = properties.get('group_id')

        if self.group_id:
            group = GroupStudents.objects.get(pk=self.group_id)
            self.initial['group'] = self.group_id
            self.fields['students'].queryset = Student.objects.filter(group=group)
            self.fields['discipline'].queryset = group.qualification.specialty.disciplines.all()


class GradebookStudentsForm(forms.ModelForm):
    ticket_number = forms.IntegerField(
        min_value=1,
        label='Номер билета'
    )

    grade = forms.ChoiceField(
        choices=GradebookStudents.ASSESSMENT_CHOICES,
        initial=GradebookStudents.ASSESSMENT_CHOICES[0][1],
        label='Оценка'
    )
    
    class Meta:
        model = GradebookStudents
        fields = ['student', 'ticket_number', 'grade']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['student'].initial = self.instance.student
            self.fields['ticket_number'].initial = self.instance.ticket_number
            self.fields['grade'].initial = self.instance.grade


            