from django_filters import rest_framework as filters
from Curriculum.models import Gradebook


class GradebookFilter(filters.FilterSet):
    """
    Фильтр для ведомостей
    """
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Gradebook
        fields = ['search']

    def filter_search(self, queryset, name, value):
        return queryset.filter(curriculum_item__discipline__name__icontains=value)


class GradeBookTeachersFilter(filters.FilterSet):
    """
    Фильтр для ведомостей
    """
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Gradebook
        fields = ['search']

    def filter_search(self, queryset, name, value):
        return queryset.filter(teacher__email__icontains=value)