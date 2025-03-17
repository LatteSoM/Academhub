from .views import *
from django.urls import path

from .views import CurriculumTableView, CurriculumDetailView, CurriculumUpdateView, CurricullumAddView
from Academhub.models.models import Curriculum

urlpatterns = [
    #
    ## Curriculum
    #

    path('curriculum/list', CurriculumTableView.as_view(), name='curriculum_list'),
    path('curriculum/<int:pk>', CurriculumDetailView.as_view(), name=Curriculum.get_urls()['url_detail']),
    path('curriculum/update/<int:pk>', CurriculumUpdateView.as_view(), name='curriculum_update'),
    path('curriculum/create/<int:pk>', CurricullumAddView.as_view(), name='curriculum_create'),

]