from django.urls import path
from Curriculum.Сontingent.views import *

urlpatterns = [
    path('discipline/', DisciplineTableView.as_view(), name='discipline_list'),
    path('discipline/<int:pk>/', DisciplineDetailView.as_view(), name='discipline_detail'),
    path('discipline/<int:pk>/update/', DisciplineUpdateView.as_view(), name='discipline_update'),
    path('discipline/create/', DisciplineCreateView.as_view(), name='discipline_create'),

    path('specialty/', SpecialtyTableView.as_view(), name='specialty_list'),
    path('specialty/<int:pk>/', SpecialtyDetailView.as_view(), name='specialty_detail'),
    path('specialty/<int:pk>/update/', SpecialtyUpdateView.as_view(), name='specialty_update'),
    path('specialty/create/', SpecialtyCreateView.as_view(), name='specialty_create'),

    path('qualification/', QualificationTableView.as_view(), name='qualification_list'),
    path('qualification/<int:pk>/', QualificationDetailView.as_view(), name='qualification_detail'),
    path('qualification/<int:pk>/update/', QualificationUpdateView.as_view(), name='qualification_update'),
    path('qualification/create/', QualificationCreateView.as_view(), name='qualification_create'),
    path('qualification/<int:qualification_id>/<int:admission_year>/', create_auto_record_book_template,
         name='create_auto_record_book_template'),
    path('qualification/<int:qualification_id>/view_record_book_template/', ViewRecordBookTemplateView.as_view(),
         name='view_record_book_template'),
    path('qualification/<int:qualification_id>/<int:admission_year>/edit_record_book_template/',
         EditRecordBookTemplateView.as_view(),
         name='edit_record_book_template'),

    path('group/', GroupTableView.as_view(), name='group_list'),
    path('group/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
    path('group/<int:pk>/update/', GroupUpdateView.as_view(), name='group_update'),
    path('group/create/', GroupCreateView.as_view(), name='group_create'),
    path('group/<int:group_id>/generate_recordbooks/', generate_group_recordbooks, name='generate_group_recordbooks'),

    path('student/', StudentTableView.as_view(), name='student_list'),
    path('student/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('student/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('student/create/', StudentCreateView.as_view(), name='student_create'),
    path('student/import/', import_students, name='import_students'),
    path('student/<int:pk>/generate_record_book/', generate_student_record_book, name='generate_student_record_book'),
    path('student/<int:pk>/view_record_book/', ViewRecordBookView.as_view(), name='view_record_book'),

    path('academ/', AcademListView.as_view(), name='academ_list'),
    path('academ/<int:pk>/update/', AcademUpdateView.as_view(), name='academ_update'),
    path('academ/return/<int:pk>/update/', AcademReturn.as_view(), name='academ_return'),

    path('expulsion/', ExpulsionListView.as_view(), name='expulsion_list'),
    path('expulsion/<int:pk>/update/', ExpelStudent.as_view(), name='expel_student'),
    path('expulsion/recover/<int:pk>/update/', RecoverStudent.as_view(), name='recover_student'),

    path('statisticks/', StatisticksView.as_view(), name='statisticks'),

    path('contingent_movement/', ContingentMovementTableView.as_view(), name='contingent_movement_list'),

]