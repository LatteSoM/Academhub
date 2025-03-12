from .views import *
from django.urls import path

from .views import AcademListView, AcademUpdateView, AcademReturn, ExpulsionListView, ExpelStudent, RecoverStudent, \
    statisticks_view, StatisticksView, generate_student_record_book, create_auto_record_book_template, \
    ContingentMovementTableView, generate_group_table, generate_course_table, generate_statistics_table, \
    generate_vacation_table, generate_movement_table, import_students

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
    ## Зачетная книжка
    #
    path('qualification/<int:qualification_id>/<int:admission_year>/record-book/save/', save_record_book_template,
         name='save_record_book_template'),
    #генерация зачетки для студента
    path('student/<int:pk>/generate-record-book/', generate_student_record_book,
         name='generate_record_book'),
    # генерация зачетки для группы
    path('group/<int:group_id>/generate-group-record-books/', generate_group_recordbooks,
         name='group_record_books_generate'),
    path('qualification/<int:qualification_id>/<int:admission_year>/record-book/auto-create/',create_auto_record_book_template,
         name='create_auto_record_book_template'),

    # Страница академа
    path('student/<int:pk>/academ-leave/', AcademUpdateView.as_view(), name='academ_leave'),
    path('academ-list/', AcademListView.as_view(), name='academ_list'),

    path('academ_return/<int:pk>/', AcademReturn.as_view(), name='academ_return'),

    # Страница движений
    path('contingent-movements/', ContingentMovementTableView.as_view(), name='contingent_movement_list'),
    path('expelled_students/', ExpulsionListView.as_view(), name='expelled_students'),
    path('student/<int:pk>/expell', ExpelStudent.as_view(), name='expel_student'),

    path('student/<int:pk>/recover', RecoverStudent.as_view(), name='student_recover'),

    # Страница статистики
    # path('statisticks/', statisticks_view, name='statisticks'),

    path('statisticks/', StatisticksView.as_view(), name='statisticks'),
    path('qualification/<int:qualification_id>/<int:admission_year>/record-book/view/', ViewRecordBookTemplateView.as_view(),
         name='view_record_book_template'),
    path('qualification/<int:qualification_id>/<int:admission_year>/<int:student_id>/record-book-student/view/', ViewRecordBookView.as_view(),
         name='view_record_book'),

    ##
    #Маршруты для генерации
    ##

    # path('contingent-movements/', ContingentMovementTableView.as_view(), name='contingent_movement_list'),
    path('generate/group-table/', generate_group_table, name='generate_group_table'),
    path('generate/course-table/<int:course>/', generate_course_table, name='generate_course_table'),
    path('generate/statistics-table/', generate_statistics_table, name='generate_statistics_table'),
    path('generate/vacation-table/', generate_vacation_table, name='generate_vacation_table'),
    path('generate/movement-table/', generate_movement_table, name='generate_movement_table'),

    path('import-students/', import_students, name='import_students'),
]
