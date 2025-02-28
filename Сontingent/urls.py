from .views import *
from django.urls import path

urlpatterns = [

    #
    ## Disciplines
    #

    path('discipline/list', DisciplineTableView.as_view(), name='discipline_list'),
    path('discipline/create', DisciplineCreateView.as_view(), name='discipline_create'),
    path('discipline/<int:pk>', DisciplineDetailView.as_view(), name='discipline_detail'),
    path('discipline/update/<int:pk>', DisciplineUpdateView.as_view(), name='discipline_update'),

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
    ##
    #

    path('qualification/<int:qualification_id>/<int:admission_year>/record-book/', create_record_book_template,
         name='create_record_book_template'),
    path('qualification/<int:qualification_id>/<int:admission_year>/record-book/save/', save_record_book_template,
         name='save_record_book_template'),
    path('qualification/<int:qualification_id>/<int:admission_year>/record-book/view/', view_record_book, name='view_record_book'),

]