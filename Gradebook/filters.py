import django_filters
from django import forms
from django.db.models import Q
import django_filters as filters
from Academhub.models import CustomUser, Gradebook, GroupStudents, Discipline

__all__ = (
    'GradebookFilter',
)


class GradebookFilter(filters.FilterSet):
    search = filters.CharFilter(
        method='filter_search',
        label='Поиск',
    )

    teachers = filters.ModelMultipleChoiceFilter(
        queryset=CustomUser.objects.filter(is_teacher=True),
        label='Учителя',
        widget=forms.CheckboxSelectMultiple
    )

    group = filters.ModelMultipleChoiceFilter(
        queryset=GroupStudents.objects.all(),
        label='Группа',
        widget=forms.CheckboxSelectMultiple
    )

    discipline = filters.ModelMultipleChoiceFilter(
        queryset=Discipline.objects.all(),
        label='Дисциплина',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Gradebook
        fields = ['group', 'teachers', 'status', 'discipline', 'semester_number']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )



class GradeBookTeachersFilter(filters.FilterSet):
    search = filters.CharFilter(
        method='filter_search',
        label='Поиск',
    )

    group = filters.ModelMultipleChoiceFilter(
        queryset=GroupStudents.objects.all(),
        label='Группа',
        widget=forms.CheckboxSelectMultiple
    )

    discipline = filters.ModelMultipleChoiceFilter(
        queryset=Discipline.objects.all(),
        label='Дисциплина',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Gradebook
        fields = ['group', 'discipline']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )
