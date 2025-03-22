from .views import *
from django.urls import path
from Academhub.utils import getpattern
from .views import GradebookGenerateView, ViewStudentsGradesForSemester, export_grades

urlpatterns = [
    #
    ## Gradebook
    #

    path('gradebook/list', GradebookTableView.as_view(), name = getpattern('Gradebook', 'list')),
    path('gradebook/create', GradebookCreateView.as_view(), name = getpattern('Gradebook', 'add')),
    path('gradebook/<int:pk>', GradebookDetailView.as_view(), name = getpattern('Gradebook', 'detail')),
    path('gradebook/update/<int:pk>', GradebookUpdateView.as_view(), name = getpattern('Gradebook', 'change')),

    path('gradebook/generate', GradebookGenerateView.as_view(), name='gradebook_generate'),
    path('gradebook/create/discipline', GradebookCreateView.as_view(), name = 'gradebook_with_discipline_create'),

    path('gradebok/view/group_grades', ViewStudentsGradesForSemester.as_view(), name = 'gradebook_view_group_grades'),

    path('gradebook/export_grades/', export_grades, name="export_grades"),

    #
    ## GradebookStudents
    #

    path('gradebook/update/<int:pk>/students/', GradebookStudentBulkUpdateView.as_view(), name='gradebookstudents_bulk_create'),

    path('gradebook/teacher/list', TeachersGradeBookTableView.as_view(), name='gradebookteacher_list'),
    path("download_report/<int:pk>/", download_report, name="download_report"),
    path('gradebook/<int:pk>/check_open/', check_and_open_gradebook, name='check_open_gradebook'),

    path('gradebook/closed/list', GradebookClosedList.as_view(), name='gradebookclosed_list'),
]