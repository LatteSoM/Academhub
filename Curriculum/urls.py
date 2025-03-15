from .views import *
from django.urls import path

from .views import CurriculumTableView, CurricullumAddView

urlpatterns = [
    #
    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/add', CurricullumAddView.as_view(), name='curriculum_create')

]