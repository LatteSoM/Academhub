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
        queryset=Student.objects.all(),
        label='Студенты',
        widget=forms.CheckboxSelectMultiple()
    )

    group_id = None

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
        properties = kwargs.pop('properties', None)
        if properties:
            self.group_id = properties['group_id']

        super().__init__(*args, **kwargs)

        if self.group_id:
            self.initial['group'] = self.group_id

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

class GradebookStudentsForm(forms.ModelForm):

    class Meta:
        model = GradebookStudents
        fields = ()