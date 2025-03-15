from .views import *
from django.urls import path

from .views import curriculum_list

urlpatterns = [
    #
    ## Curriculum
    #

    path('curriculum/list', curriculum_list, name='curriculums_list'),

]