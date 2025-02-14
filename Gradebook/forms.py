from django import forms
from Academhub.models import Gradebook, GradebookStudents, CustomUser, Discipline, Student, GroupStudents


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
    group = forms.ModelChoiceField(
        queryset=GroupStudents.objects.all(),
        label='Группа'
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        label='Студенты',
    )

    class Meta:
        """
        Метакласс для настройки формы.
        """
        model = Gradebook
        fields = ['name', 'semester_number', 'teacher', 'discipline', 'group', 'students']

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
        elif self.instance.pk:
            self.initial['group'] = self.group_id
            self.fields['students'].queryset = Student.objects.filter(group__id=self.group_id)

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
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     if 'instance' in kwargs:
    #         self.fields['student'].initial = kwargs['instance'].student