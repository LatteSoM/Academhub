from django.shortcuts import render
# from parser_for_plx import RUP_parser
from django.shortcuts import render

from Academhub.generic.generic import ObjectDetailView, ObjectUpdateView
from .forms import GetPlxForm
from Academhub.models import Curriculum
from .tables import CurriculumTable
from Academhub.generic import ObjectTableView, ObjectCreateView, ImportViewMixin
from .filters import CurriculumQualificationsFilter
# Create your views here.


__all__ = (
    'CurriculumTableView',
    'CurricullumAddView',
    'CurriculumDetailView',
    'CurriculumUpdateView',
)

class CurriculumTableView(ImportViewMixin, ObjectTableView):
    """
    Класс для отображения таблицы учебных журналов.
    """
    table_class = CurriculumTable
    queryset = Curriculum.objects.all()
    filterset_class = CurriculumQualificationsFilter
    form_import = GetPlxForm
    template_name = 'Curriculum/list/curriculums.html'


class CurricullumAddView(ObjectCreateView):
    model = Curriculum
    form_class = GetPlxForm
    


class CurriculumDetailView(ObjectDetailView):
    model = Curriculum


    fieldset = {
    'Год поступления': [
        'admission_year', 'qualification'
        ],
    }


class CurriculumUpdateView(ObjectUpdateView):
    form_class = Curriculum
    queryset = Curriculum.objects.all()