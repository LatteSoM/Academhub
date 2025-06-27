from .views import *
from django.urls import path
from .api.complete_set import *
from .api.releases_from_curriculums import *
from Academhub.utils import getpattern
from .views import *

urlpatterns = [
    #    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/add', CurricullumAddView.as_view(), name='curriculum_create'),
    path('curriculum/edit', CurriculumEditableFormView.as_view(), name='curriculum_edit_form'),
    # path('curriculum/<int:pk>', CurriculumDetail.as_view(), name= getpattern('Curriculum', 'detail')),

    path('releases/list/', ReleaseFromCurriculumView.as_view(), name=getpattern('ReleaseFromCurriculum', 'list')),
    path('releases/add/', ReleaseFromCurriculumCreateView.as_view(), name=getpattern('ReleaseFromCurriculum', 'add')),
    path('releases/detail/<int:pk>/', ReleaseFromCurriculumDetailView.as_view(),
         name=getpattern('ReleaseFromCurriculum', 'detail')),

    # AJAX API
    ## complete_set
    path('api/study-plans/', get_study_plans, name='get_study_plans'),
    path('api/courses_and_groups/', get_courses_and_groups_for_study_plan, name='get_courses_and_groups_for_study_plan'),
    path('api/courses/', get_courses_for_study_plan, name='get_courses_for_study_plan'),
    path('api/disciplines_by_curriculum_course_term/', get_disciplines_by_curriculum_course_term,
         name='get_disciplines_by_curriculum_course_term'),
    path('api/disciplines_by_curriculum_course_term_for_attestation/', get_disciplines_by_curriculum_course_term_for_attestation,
         name='get_disciplines_by_curriculum_course_term_for_attestations'),
    path('api/import_teachers_excel/', import_teachers_excel_view, name='import_teachers_excel'),
    path('api/save-all-changes/', save_teachers_for_groups_and_disciplines,
         name='save_teachers_for_groups_and_disciplines'),
    path('api/save-attestation-periods/', save_periods_for_groups_and_disciplines,
         name='save_periods_for_groups_and_disciplines'),

    ## releases_from_curriculum
    path('api/curriculums_by_spec_id/',
         get_study_plans_by_qualification,
         name='get_curriculums_by_spec'),

    path('api/create_new_release_from_curriculum/',
         create_new_release_from_curriculum,
         name='create_new_release_from_curriculum'),
    path('api/get_weeks_count_for_release/',
         get_weeks_count_for_release,
         name='get_weeks_count_for_release'),

    path('api/get_groups_by_curriculum_id/',
         get_groups_by_curriculum_id,
         name='get_groups_by_curriculum_id'),

    path('api/get_disciplines_and_teacher_for_theme/',
         get_disciplines_and_teacher_for_theme,
         name='get_disciplines_and_teacher_for_theme'),
    path('api/get_disciplines_with_cells/',
         get_disciplines_with_cells,
         name='get_disciplines_with_cells'),
    path('api/save_all_cells/',
         save_all_cells,
         name='save_all_cells'),


    path("curriculum/complete_set/", CompleteSetCurriculum.as_view(), name='curriculum_complete_set'),
    # Placeholder URL for setting attestation periods - View needs implementation
    path("attestation/set-period/", SetAttestationPeriodView.as_view(), name='set_attestation_period'),


    path('<int:pk>/preview/', CurriculumPreviewView.as_view(), name='curriculum_preview'),
    path('<int:pk>/delete/', CurriculumDeleteView.as_view(), name='curriculum_delete'),
]
