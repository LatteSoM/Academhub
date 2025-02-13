from .views import *
from django.urls import path

urlpatterns = [
    #
    ## Specialty
    #

    path('specialty/list', SpecialtyTableView.as_view(), name='specialty_list'),
    path('specialty/create', SpecialtyCreateView.as_view(), name='specialty_create'),
    path('specialty/<int:pk>', SpecialtyDetailView.as_view(), name='specialty_detail'),
    path('specialty/update/<int:pk>', SpecialtyUpdateView.as_view(), name='specialty_update'),

    #
    ## Qualification
    #

    path('qualification/list', QualificationTableView.as_view(), name='qualification_list'),
    path('qualification/create', QualificationCreateView.as_view(), name='qualification_create'),
    path('qualification/<int:pk>', QualificationDetailView.as_view(), name='qualification_detail'),
    path('qualification/update/<int:pk>', QualificationUpdateView.as_view(), name='qualification_update'),


    #
    ## Group
    #

    path('group/list', GroupTableView.as_view(), name='groupstudents_list'),
    path('group/create', GroupCreateView.as_view(), name='groupstudents_create'),
    path('group/<int:pk>', GroupDetailView.as_view(), name='groupstudents_detail'),
    path('group/update/<int:pk>', GroupUpdateView.as_view(), name='groupstudents_update'),
    
    #
    ## Student
    #
    
    path('student/list', StudentTableView.as_view(), name='student_list'),
    path('student/create', StudentCreateView.as_view(), name='student_create'),
    path('student/<int:pk>', StudentDetailView.as_view(), name='student_detail'),
    path('student/update/<int:pk>', StudentUpdateView.as_view(), name='student_update'),

    #
    # Gradebook
    #

    path('gradebook/list', GradebooktableView.as_view(), name='gradebook_list'),

]