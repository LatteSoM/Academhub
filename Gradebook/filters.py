from django_filters import FilterSet, CharFilter

from Academhub.models import *

__all__ = (
    'GradebookFilter',
)


class GradebookFilter(FilterSet):
    search = CharFilter(method='filter_search',
                        label='Поиск')

    class Meta:
        model = Gradebook
        fields = ['group', 'teacher', 'status', 'discipline', 'semester_number']
