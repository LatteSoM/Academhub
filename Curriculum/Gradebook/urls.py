from django.urls import path
from Curriculum.Gradebook.views import *

urlpatterns = [
    path('', GradebookTableView.as_view(), name='gradebook_list'),
    path('teachers/', TeachersGradeBookTableView.as_view(), name='gradebook_teachers_list'),
    path('<int:pk>/', GradebookDetailView.as_view(), name='gradebook_detail'),
    path('<int:pk>/update/', GradebookUpdateView.as_view(), name='gradebook_update'),
    path('create/', GradebookCreateView.as_view(), name='gradebook_create'),
    path('download_report/<int:pk>/', download_report, name='download_gradebook_report'),
    path('check_and_open_gradebook/<int:pk>/', check_and_open_gradebook, name='check_and_open_gradebook'),
    path('update_students/<int:pk>/', GradebookStudentBulkUpdateView.as_view(), name='gradebook_students_update'),
]