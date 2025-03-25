from .views import *
from django.urls import path
from Academhub.utils import getpermission, getpattern
from .views import AcademListView, AcademUpdateView, AcademReturn, ExpulsionListView, ExpelStudent, RecoverStudent, \
    StatisticksView, generate_student_record_book, create_auto_record_book_template, \
    ContingentMovementTableView, generate_group_table, generate_course_table, generate_statistics_table, \
    generate_vacation_table, generate_movement_table, \
    generate_student_record_book, create_auto_record_book_template

urlpatterns = [

     #
     ## Disciplines
     #

     path('discipline/list', DisciplineTableView.as_view(), name=getpattern('Discipline', 'list')),
     path('discipline/add', DisciplineCreateView.as_view(), name=getpattern('Discipline', 'add')),
     path('discipline/<int:pk>', DisciplineDetailView.as_view(), name=getpattern('Discipline', 'detail')),
     path('discipline/update/<int:pk>', DisciplineUpdateView.as_view(), name=getpattern('Discipline', 'change')),

     #
     ## Specialty
     #

     path('specialty/list', SpecialtyTableView.as_view(), name=getpattern('Specialty', 'list')),
     path('specialty/add', SpecialtyCreateView.as_view(), name=getpattern('Specialty', 'add')),
     path('specialty/<int:pk>', SpecialtyDetailView.as_view(), name=getpattern('Specialty', 'detail')),
     path('specialty/update/<int:pk>', SpecialtyUpdateView.as_view(), name=getpattern('Specialty', 'change')),

     #
     ## Qualification
     #

     path('qualification/list', QualificationTableView.as_view(), name=getpattern('Qualification', 'list')),
     path('qualification/add', QualificationCreateView.as_view(), name=getpattern('Qualification', 'add')),
     path('qualification/<int:pk>', QualificationDetailView.as_view(), name=getpattern('Qualification', 'detail')),
     path('qualification/update/<int:pk>', QualificationUpdateView.as_view(), name=getpattern('Qualification', 'change')),


     #
     ## Group
     #

     path('group/list', GroupTableView.as_view(), name=getpattern('GroupStudents', 'list')),
     path('group/add', GroupCreateView.as_view(), name=getpattern('GroupStudents', 'add')),
     path('group/<int:pk>', GroupDetailView.as_view(), name=getpattern('GroupStudents', 'detail')),
     path('group/update/<int:pk>', GroupUpdateView.as_view(), name=getpattern('GroupStudents', 'change')),
     path('group/promote-students/<int:pk>', PromoteGroupStudentsView.as_view(), name='promote_group_students_form'),

     #
     ## Student
     #

     path('student/list', StudentTableView.as_view(), name=getpattern('CurrentStudent', 'list')),
     path('student/add', StudentCreateView.as_view(), name=getpattern('CurrentStudent', 'add')),
     path('student/<int:pk>', StudentDetailView.as_view(), name=getpattern('CurrentStudent', 'detail')),
     path('student/update/<int:pk>', StudentUpdateView.as_view(), name=getpattern('CurrentStudent', 'change')),


     # Студенты в академическом отпуске
    path('student/<int:pk>/academ-leave/', AcademUpdateView.as_view(), name='academ_leave'),
    path('student/academ/list', AcademListView.as_view(), name=getpattern('AcademStudent', 'list')),
    path('academ_return/<int:pk>/', AcademReturn.as_view(), name='academ_return'),


     # Студенты отчисленные

     path('student/explusion/list', ExpulsionListView.as_view(), name=getpattern('ExpulsionStudent', 'list')),
     path('expelled_students/', ExpulsionListView.as_view(), name='expelled_students'),
     path('student/<int:pk>/expell', ExpelStudent.as_view(), name='expel_student'),

     # Страница движений
     path('contingent-movements/', ContingentMovementTableView.as_view(), name=getpattern('ContingentMovement', 'list')),

     path('student/<int:pk>/recover', RecoverStudent.as_view(), name='student_recover'),

     # Страница статистики

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

     #
     ## Зачетная книжка
     #
     path('qualification/<int:qualification_id>/<int:admission_year>/record-book/save/', save_record_book_template, name='save_record_book_template'),
     #генерация зачетки для студента
     path('student/<int:pk>/generate-record-book/', generate_student_record_book, name='generate_record_book'),
     # генерация зачетки для группы
     path('group/<int:group_id>/generate-group-record-books/', generate_group_recordbooks, name='group_record_books_generate'),
     path('qualification/<int:qualification_id>/<int:admission_year>/record-book/auto-add/', create_auto_record_book_template, name='create_auto_record_book_template'),
]
