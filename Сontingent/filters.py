from cProfile import label

from django import forms
from django.db.models import Q

from Academhub.models import Qualification, Specialty, GroupStudents, Student, Discipline
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ModelMultipleChoiceFilter, ChoiceFilter


__all__ = (
    'GroupFilter',
    'StudentFilter',
    'SpecialtyFilter',
    'DisciplineFilter',
    'QualificationFilter',
)

class DisciplineFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    qualification = ModelMultipleChoiceFilter(
        queryset=Qualification.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        label='Квалификация',
    )

    groups = ModelMultipleChoiceFilter(
        queryset=GroupStudents.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        label='Группы',
    )

    class Meta:
        model = Discipline
        fields = [
            'specialty',
            'groups',
        ]

class QualificationFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = Qualification
        fields = ['short_name', 'name']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(short_name__icontains=value) |
            Q(name__icontains=value)
        )

class SpecialtyFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = Specialty
        fields = ['code', 'name']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(code__icontains=value) |
            Q(name__icontains=value)
        )

class GroupFilter(FilterSet):
    qualification = ModelChoiceFilter(queryset=Qualification.objects.all(), label='Квалификация')
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = GroupStudents
        fields = ['number', 'qualification']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(qualification__short_name__icontains=value) |
            Q(qualification__name__icontains=value)
        )

class StudentFilter(FilterSet):
    search = CharFilter(method='filter_search',
                        label='Поиск')

    COURSE_CHOICES = (
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4)
    )

    course = ChoiceFilter(choices=COURSE_CHOICES, label='Курс')

    group = ModelMultipleChoiceFilter(
        widget=forms.CheckboxSelectMultiple,
        label='Группа',
        queryset=GroupStudents.objects.all(),
    )

    education_base = MultipleChoiceFilter(
        label='База образования',
        widget=forms.CheckboxSelectMultiple,
        choices = Student.EDUCATION_BASE_CHOICES
    )

    education_basis = MultipleChoiceFilter(
        label='Основа образования',
        choices = Student.EDUCATION_BASIS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Student
        fields = ['course', 'group', 'education_base', 'education_basis']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(phone__icontains=value) |
            Q(course__icontains=value)
        )


