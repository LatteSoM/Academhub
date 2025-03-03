from cProfile import label

from django import forms
from django.db.models import Q
from django.db.models.fields import DateField

from Academhub.models import Qualification, Specialty, GroupStudents, Student, Discipline
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ModelMultipleChoiceFilter, ChoiceFilter, \
    MultipleChoiceFilter, DateFilter

__all__ = (
    'GroupFilter',
    'StudentFilter',
    'SpecialtyFilter',
    'DisciplineFilter',
    'QualificationFilter',
)

class DisciplineFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

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

class AcademFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    COURSE_CHOICES = (
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4)
    )

    REASONS_OF_ACADEM_CHOICES = (
        ("с/о", "с/о"),
    )

    left_course = ChoiceFilter(choices=COURSE_CHOICES, label='Курс, с которого ушел')

    group = ModelMultipleChoiceFilter(
        widget=forms.CheckboxSelectMultiple,
        label='Группа',
        queryset=GroupStudents.objects.all(),
    )

    education_base = MultipleChoiceFilter(
        label='База образования',
        widget=forms.CheckboxSelectMultiple,
        choices=Student.EDUCATION_BASE_CHOICES
    )

    reason_of_academ = ChoiceFilter(choices=REASONS_OF_ACADEM_CHOICES, label='Причины ухода в академ')

    # TODO: Add filter for a year

    class Meta:
        model = Student
        fields = ['left_course', 'group', 'education_base', 'reason_of_academ']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(phone__icontains=value) |
            Q(course__icontains=value)
        )

class ExpulsionFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    COURSE_CHOICES = (
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4)
    )

    REASONS_OF_EXPELLING_CHOICES = (
        ("с/ж", "с/ж"),
        ("Перевод", "Перевод"),
        ("Смерть", "Смерть"),
        # TODO: Выяснить про другие причины
    )

    left_course = ChoiceFilter(choices=COURSE_CHOICES, label='Курс, с которого ушел')

    group = ModelMultipleChoiceFilter(
        widget=forms.CheckboxSelectMultiple,
        label='Группа',
        queryset=GroupStudents.objects.all(),
    )

    education_base = MultipleChoiceFilter(
        label='База образования',
        widget=forms.CheckboxSelectMultiple,
        choices=Student.EDUCATION_BASE_CHOICES
    )

    education_basis = MultipleChoiceFilter(
        label='Основа образования',
        choices=Student.EDUCATION_BASIS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    reason_of_expulsion = MultipleChoiceFilter(choices=REASONS_OF_EXPELLING_CHOICES,
                                               label="Причина отчисления", widget=forms.CheckboxSelectMultiple)

    # TODO: Сделать фильтр на год

    qualification = ModelChoiceFilter(queryset=Qualification.objects.all(), label='Квалификация')
    specialty = ModelChoiceFilter(queryset=Specialty.objects.all(), label='Специальность')

