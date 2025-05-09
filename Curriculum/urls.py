from django.urls import path

from Academhub.utils import getpattern
from .api.v1 import *
from .views import *
from .views import SetAttestationPeriodView, ReleaseFromCurriculumView, ReleaseFromCurriculumCreateView

urlpatterns = [
    #    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/add', CurricullumAddView.as_view(), name='curriculum_create'),
    path('curriculum/edit', CurriculumEditableFormView.as_view(), name='curriculum_edit_form'),
    # path('curriculum/<int:pk>', CurriculumDetail.as_view(), name= getpattern('Curriculum', 'detail')),

    path('releases/list', ReleaseFromCurriculumView.as_view(), name=getpattern('ReleaseFromCurriculum', 'detail')),
    path('releases/add', ReleaseFromCurriculumCreateView.as_view(), name=getpattern('ReleaseFromCurriculum', 'add')),

    # AJAX API
    path('api/study-plans/', get_study_plans, name='get_study_plans'),
    path('api/courses_and_groups/', get_courses_for_study_plan, name='get_courses_for_study_plan'),
    path('api/disciplines_by_curriculum_course_term/', get_disciplines_by_curriculum_course_term,
         name='get_disciplines_by_curriculum_course_term'),
    path('api/disciplines_by_curriculum_course_term_for_attestation/', get_disciplines_by_curriculum_course_term_for_attestation,
         name='get_disciplines_by_curriculum_course_term_for_attestations'),
    path('api/import_teachers_excel/', import_teachers_excel_view, name='import_teachers_excel'),
    path('api/save-all-changes/', save_teachers_for_groups_and_disciplines,
         name='save_teachers_for_groups_and_disciplines'),
    path('api/save-attestation-periods/', save_periods_for_groups_and_disciplines,
         name='save_periods_for_groups_and_disciplines'),


    path("curriculum/complete_set/", CompleteSetCurriculum.as_view(), name='curriculum_complete_set'),
    # Placeholder URL for setting attestation periods - View needs implementation
    path("attestation/set-period/", SetAttestationPeriodView.as_view(), name='set_attestation_period'),


    path('<int:pk>/preview/', CurriculumPreviewView.as_view(), name='curriculum_preview'),
    path('<int:pk>/delete/', CurriculumDeleteView.as_view(), name='curriculum_delete'),
]
