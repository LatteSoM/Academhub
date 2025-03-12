from django import forms
from Academhub.models import Gradebook, GradebookStudents, CustomUser, Discipline, Student, GroupStudents

__all__ = (
    'GradebookForm',
    'GradebookStudentsForm',
)

class GradebookForm(forms.ModelForm):
    """
    Форма для создания и редактирования записей в журнале оценок.
    """
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
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        """
        Метакласс для настройки формы.
        """
        model = Gradebook
        fields = ['name', 'semester_number', 'type_of_grade_book', 'amount_of_days_for_closing', 'teachers', 'group', 'discipline', 'students']

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.
        """
        properties = kwargs.pop('properties', {})
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.group_id = properties.get('group_id', self.instance.group.pk)
            if self.group_id == '':
                self.group_id = self.instance.group.pk
        else:
            self.group_id = properties.get('group_id', None)
        
        if self.group_id:
            self.initial['group'] = self.group_id
            self.fields['students'].queryset = Student.objects.filter(group__id=self.group_id)
            
            group = GroupStudents.objects.filter(pk=self.group_id)

            if  group.exists():
                group = group.first()

                specialty = group.qualification.specialty
                self.fields['discipline'].queryset = specialty.disciplines.all()


        elif self.instance.pk:
            self.initial['group'] = self.group_id
            self.fields['students'].queryset = Student.objects.filter(group__id=self.group_id)
            self.fields['discipline'].queryset = self.instance.group.qualification.specialty.disciplines.all()

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


            