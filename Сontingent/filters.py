from cProfile import label

from django import forms
from django.db.models import Q
from .models import StudentDTO, QualificationDTO, SpecializationDTO, GroupDTO
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ModelMultipleChoiceFilter

class QualificationFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = QualificationDTO
        fields = ['union_name', 'name']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(union_name__icontains=value) |
            Q(name__icontains=value)
        )

class SpecializationFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = SpecializationDTO
        fields = ['code', 'name']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(code__icontains=value) |
            Q(name__icontains=value)
        )

class GroupFilter(FilterSet):
    qualification = ModelChoiceFilter(queryset=QualificationDTO.objects.all(), label='Квалификация')
    specialization = ModelChoiceFilter(queryset=SpecializationDTO.objects.all(), label='Специальность')
    search = CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = GroupDTO
        fields = ['qualification', 'specialization']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(qualification__union_name__icontains=value) |
            Q(qualification__name__icontains=value) |
            Q(specialization__code__icontains=value) |
            Q(specialization__name__icontains=value)
        )

class StudentFilter(FilterSet):
    search = CharFilter(method='filter_search', 
                        label='Поиск')

    group = ModelMultipleChoiceFilter(
        widget=forms.CheckboxSelectMultiple,
        label='Группа',
        queryset=GroupDTO.objects.all(),
    )

    class Meta:
        model = StudentDTO
        fields = ['phone', 'course', 'group']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(phone__icontains=value) |
            Q(course__icontains=value)
        )