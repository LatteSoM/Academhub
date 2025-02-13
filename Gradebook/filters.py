from django.db.models import Q
import django_filters as filters
from Academhub.models import CustomUser, Gradebook, GradebookStudents, Discipline

__all__ = (
    'GradebookFilter',
)


class GradebookFilter(filters.FilterSet):
    search = filters.CharFilter(
        method='filter_search',
        label='Поиск'
    )

    teacher = filters.ModelMultipleChoiceFilter(
        queryset=CustomUser.objects.filter(is_teacher=True), 
        label='Учитель'
    )

    group = filters.ModelMultipleChoiceFilter(
        queryset=GradebookStudents.objects.all(),
        label='Группа',
    )

    discipline = filters.ModelMultipleChoiceFilter(
        queryset=Discipline.objects.all(),
        label='Дисциплина',
    )

    class Meta:
        model = Gradebook
        fields = ['group', 'teacher', 'status', 'discipline', 'semester_number']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )
