from django import forms

from Curriculum.models import Gradebook, GradebookStudents


class GradebookForm(forms.ModelForm):
    """
    Форма для ведомости
    """

    class Meta:
        model = Gradebook
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['students'].queryset = self.instance.group.student_set.all()


class GradebookStudentsForm(forms.ModelForm):
    """
    Форма для ведомости
    """

    class Meta:
        model = GradebookStudents
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)