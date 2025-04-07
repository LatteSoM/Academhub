from django.urls import path

from Academhub.utils import getpattern
from .views import *
from .api.v1 import *
from .views import CurriculumPreviewView

urlpatterns = [
    #    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/add', CurricullumAddView.as_view(), name='curriculum_create'),
    path('curriculum/edit', CurriculumEditableFormView.as_view(), name='curriculum_edit_form'),
    # path('curriculum/<int:pk>', CurriculumDetail.as_view(), name= getpattern('Curriculum', 'detail')),

    # Пофиксим view и норм
    # from .views import CompleteSetCurriculum
    # path("curriculum/complete_set", CompleteSetCurriculum.as_view(), name='curriculum_complete_set'),

    #AJAX API
    path('api/study-plans/', get_study_plans, name='get_study_plans'),
    path('api/courses_and_groups/', get_courses_for_study_plan, name='get_courses_for_study_plan'),
    path('api/disciplines_by_curriculum_course_term/', get_disciplines_by_curriculum_course_term, name='get_disciplines_by_curriculum_course_term'),


    path('curriculum/<int:pk>/discipline/<int:discipline_id>/course/<int:course_number>/term/<int:term_number>', AddTeacher2DisciplineOnTerm.as_view(), name='curriculum_add_teacher'),
    path('curriculum/<int:pk>/<int:discipline_id>/<int:course_number>/<int:term_number>/del/<int:teacher_id>', RemoveTeacherFromDiscipline.as_view(), name='remove_teacher_from_discipline'),
    path('curriculum/<int:pk>/<int:discipline_id>/<int:course_number>/<int:term_number>/add/<int:teacher_id>', AddTeacherToDiscipline.as_view(), name='add_teacher_to_discipline'),
    path('<int:pk>/preview/', CurriculumPreviewView.as_view(), name='curriculum_preview'),
    path('<int:pk>/delete/', CurriculumDeleteView.as_view(), name='curriculum_delete'),
]
