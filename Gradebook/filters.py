import django_filters as filters
from django import forms
from django.db.models import Q, Min, Max

from Academhub.models import CustomUser, Gradebook, GroupStudents, Discipline

__all__ = (
    'GradebookFilter',
    'ClosedGradebookFilter',
    'GradeBookTeachersFilter'
)


class GradebookFilter(filters.FilterSet):
    search = filters.CharFilter(
        method='filter_search',
        label='Поиск',
    )

    teachers = filters.ModelMultipleChoiceFilter(
        queryset=CustomUser.objects.filter(is_teacher=True, is_active=True),
        label='Учителя',
        widget=forms.CheckboxSelectMultiple
    )

    group = filters.ModelMultipleChoiceFilter(
        queryset=GroupStudents.objects.filter(is_active=True),
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
        fields = ['group', 'teachers', 'status', 'discipline', 'semester_number', 'type_of_grade_book']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )


class ClosedGradebookFilter(filters.FilterSet):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем минимальный и максимальный год из date_of_closing
        min_year = Gradebook.objects.aggregate(min_year=Min('date_of_closing__year'))['min_year']
        max_year = Gradebook.objects.aggregate(max_year=Max('date_of_closing__year'))['max_year']
        if min_year and max_year:
            years = [(year, year) for year in range(min_year, max_year + 1)]
            self.filters['closing_year'].extra['choices'] = years

    closing_year = filters.ChoiceFilter(
        field_name='date_of_closing__year',
        lookup_expr='exact',
        label='Год закрытия',
        empty_label='Выберите год'
    )

    class Meta:
        model = Gradebook
        fields = ['group', 'teachers', 'discipline', 'semester_number', 'type_of_grade_book', 'closing_year']

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
        queryset=GroupStudents.objects.filter(is_active=True),
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
