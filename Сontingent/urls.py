from .views import *
from django.urls import path

urlpatterns = [
    path('qualification/list', QualificationTableView.as_view(), name='qualification_list'),

    path('specialization/list', SpecializationTableView.as_view(), name='specialization_list'),
    
    path('group/list', GroupTableView.as_view(), name='group_list'),
    
    #
    ## Student
    #
    
    path('student/list', StudentTableView.as_view(), name='studentdto_list'),
    path('student/create', StudentCreateView.as_view(), name='studentdto_create'),
    path('student/<int:pk>', StudentDetailView.as_view(), name='studentdto_detail'),
    path('student/update/<int:pk>', StudentUpdateView.as_view(), name='studentdto_update'),
    path('student/delete/<int:pk>', StudentDeleteView.as_view(), name='studentdto_delete'),
]