from cProfile import label

from django import forms
from django.db.models import Q

from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ModelMultipleChoiceFilter, ChoiceFilter

from Academhub.models import Qualification, Specialty, GroupStudents, Student

__all__ = (
    'GroupFilter',
    'StudentFilter',
    'SpecialtyFilter',
    'QualificationFilter',
)


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
    specialization = ModelChoiceFilter(queryset=Specialty.objects.all(), label='Специальность')
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = GroupStudents
        fields = ['number', 'qualification']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(qualification__short_name__icontains=value) |
            Q(qualification__name__icontains=value) |
            Q(specialization__code__icontains=value) |
            Q(specialization__name__icontains=value)
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

    class Meta:
        model = Student
        fields = ['course', 'group']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(phone__icontains=value) |
            Q(course__icontains=value)
        )