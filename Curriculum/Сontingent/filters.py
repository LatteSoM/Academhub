from django_filters import FilterSet, CharFilter, NumberFilter, DateFilter

# from Curriculum.models import Discipline, Qualification, Specialty, GroupStudents, Student, ContingentMovement

# TODO: Update filters to use new models.

# class DisciplineFilter(FilterSet):
#     """
#     Фильтр для дисциплин
#     """
#
#     class Meta:
#         model = Discipline
#         fields = ['name']
#
#
# class QualificationFilter(FilterSet):
#     """
#     Фильтр для квалификаций
#     """
#     search = CharFilter(method='filter_search')
#
#     class Meta:
#         model = Qualification
#         fields = ['search']
#
#     def filter_search(self, queryset, name, value):
#         return queryset.filter(name__icontains=value)
#
#
# class SpecialtyFilter(FilterSet):
#     """
#     Фильтр для специальностей
#     """
#     search = CharFilter(method='filter_search')
#
#     class Meta:
#         model = Specialty
#         fields = ['search']
#
#     def filter_search(self, queryset, name, value):
#         return queryset.filter(name__icontains=value)
#
#
# class GroupFilter(FilterSet):
#     """
#     Фильтр для групп
#     """
#     search = CharFilter(method='filter_search')
#
#     class Meta:
#         model = GroupStudents
#         fields = ['search']
#
#     def filter_search(self, queryset, name, value):
#         return queryset.filter(name__icontains=value)
#
#
# class StudentFilter(FilterSet):
#     """
#     Фильтр для студентов
#     """
#     search = CharFilter(method='filter_search')
#
#     class Meta:
#         model = Student
#         fields = ['search']
#
#     def filter_search(self, queryset, name, value):
#         return queryset.filter(last_name__icontains=value)
#
#
# class AcademFilter(FilterSet):
#     """
#     Фильтр для академических отпусков
#     """
#     search = CharFilter(method='filter_search')
#
#     class Meta:
#         model = Student
#         fields = ['search']
#
#     def filter_search(self, queryset, name, value):
#         return queryset.filter(student__last_name__icontains=value)
#
#
# class ExpulsionFilter(FilterSet):
#     """
#     Фильтр для отчисленых студентов
#     """
#
#     class Meta:
#         model = Student
#         fields = ['group']
#
#
# class ContingentMovementFilter(FilterSet):
#     """
#     Фильтр для движения контингента студентов
#     """
#
#     class Meta:
#         model = ContingentMovement
#         fields = '__all__'