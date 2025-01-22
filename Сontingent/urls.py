from .views import *
from django.urls import path

urlpatterns = [
    path('qualification/list', QualificationTableView.as_view(), name='qualification_list'),
    path('specialization/list', SpecializationTableView.as_view(), name='specialization_list'),
    path('group/list', GroupTableView.as_view(), name='group_list'),
    path('student/list', StudentTableView.as_view(), name='student_list'),
]