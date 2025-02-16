from .views import *
from django.urls import path

urlpatterns = [
    #
    ## Gradebook
    #

    path('gradebook/list', GradebookTableView.as_view(), name='gradebook_list'),
    path('gradebook/create', GradebookCreateView.as_view(), name='gradebook_create'),
    path('gradebook/<int:pk>', GradebookDetailView.as_view(), name='gradebook_detail'),
    path('gradebook/update/<int:pk>', GradebookUpdateView.as_view(), name='gradebook_update'),

    #
    ## GradebookStudents
    #

    path('gradebook/update/<int:pk>/students/', GradebookStudentBulkUpdateView.as_view(), name='gradebookstudents_bulk_create')
]