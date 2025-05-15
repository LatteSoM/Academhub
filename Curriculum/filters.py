import django_filters as filters
from django import forms
from django.db.models import Q

from Academhub.models import Curriculum, Qualification, ReleaseFromCurriculum

__all__ = (
    'CurriculumQualificationsFilter',
    'ReleaseFromCurriculumFilter',
)

class CurriculumQualificationsFilter(filters.FilterSet):
    qualification = filters.ModelMultipleChoiceFilter(
        queryset=Qualification.objects.all(),
        label='Квалификации',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Curriculum
        fields = ['qualification']


class ReleaseFromCurriculumFilter(filters.FilterSet):
    qualification = filters.ModelChoiceFilter(queryset=Qualification.objects.all(), label='Квалификация')
    search = filters.CharFilter(method='filter_search', label='Поиск')

    class Meta:
        model = ReleaseFromCurriculum
        fields = ['course', 'qualification']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(qualification__short_name__icontains=value) |
            Q(qualification__name__icontains=value)
        )

