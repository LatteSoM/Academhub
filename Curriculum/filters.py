from django import forms
from django.db.models import Q
import django_filters as filters
from Academhub.models import Curriculum, Qualification

__all__ = (
    'GradebookFilter',
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
