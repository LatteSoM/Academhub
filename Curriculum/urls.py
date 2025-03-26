from django.urls import path

from Academhub.utils import getpattern
from .views import CurriculumTableView, CurricullumAddView, CurriculumEditableFormView, AddTeacher2DisciplineOnTerm

urlpatterns = [
    #    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/add', CurricullumAddView.as_view(), name='curriculum_create'),
    path('curriculum/edit', CurriculumEditableFormView.as_view(), name='curriculum_edit_form'),
    path('curriculum/<int:pk>', AddTeacher2DisciplineOnTerm.as_view(), name= getpattern('Curriculum', 'detail')),

]