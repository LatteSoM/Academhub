from django.urls import path

from Academhub.utils import getpattern
from .views import *

urlpatterns = [
    #    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/add', CurricullumAddView.as_view(), name='curriculum_create'),
    path('curriculum/edit', CurriculumEditableFormView.as_view(), name='curriculum_edit_form'),
    path('curriculum/<int:pk>', CurriculumDetail.as_view(), name= getpattern('Curriculum', 'detail')),
    path('curriculum/<int:pk>/discipline/<int:discipline_id>/course/<int:course_number>/term/<int:term_number>', AddTeacher2DisciplineOnTerm.as_view(), name='curriculum_add_teacher'),
    path('curriculum/<int:pk>/<int:discipline_id>/<int:course_number>/<int:term_number>/del/<int:teacher_id>', RemoveTeacherFromDiscipline.as_view(), name='remove_teacher_from_discipline'),
    path('curriculum/<int:pk>/<int:discipline_id>/<int:course_number>/<int:term_number>/add/<int:teacher_id>', AddTeacherToDiscipline.as_view(), name='add_teacher_to_discipline'),
]