import json

from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
# from parser_for_plx import RUP_parser
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, DetailView

from Academhub.generic import ObjectTableView, ObjectCreateView, ImportViewMixin, ObjectTemplateView, ObjectDetailView
from Academhub.models import Curriculum, ClockCell, Category, StudyCycle, Discipline
from .filters import CurriculumQualificationsFilter
from .forms.GetPlxForm import GetPlxForm
from .forms.EditableCurriculumForm import EditableCurriculumForm
from .tables import CurriculumTable

__all__ = (
    'CurriculumTableView',
    'CurricullumAddView',
    'CurriculumEditableFormView',
    'AddTeacher2DisciplineOnTerm'
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

    def generate_form_import(self, *args, **kwargs):
        return self.form_import(*args, **kwargs, request=self.request)

    def form_valid(self, form):
        """
        Вызывается при успешной отправке формы импорта.
        Перенаправляет на страницу редактирования учебного плана.
        """
        form.save()
        return HttpResponseRedirect(reverse('curriculum_edit_form'))

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, валидирует и сохраняет form."""
        self._form = self.save_from_import(request.POST, request.FILES)

        if self._form.is_valid():
            return redirect('curriculum_edit_form')
        else:
            response = super().post(request, *args, **kwargs)
            return response


class CurricullumAddView(ObjectCreateView):
    model = Curriculum
    form_class = GetPlxForm

class CurriculumEditableFormView(TemplateView):
    template_name = 'Curriculum/editable_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uploaded_data_json = self.request.session.get('uploaded_data')
        if uploaded_data_json:
            form = EditableCurriculumForm(uploaded_data_json)
            context['editable_form'] = form

        context['semester_list'] = ["1", "2", "3", "4", "5", "6", "7", "8"]
        return context

    def post(self, request, *args, **kwargs):
        uploaded_data_json = request.session.get('uploaded_data')
        form = EditableCurriculumForm(uploaded_data_json, request.POST)
        if self.form_valid(form):
            return redirect('curriculum_list')
        else:
            context = self.get_context_data(**kwargs)
            context['editable_form'] = form
            return self.render_to_response(context)

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Успешное сохранение учебного плана"
        )
        return redirect('curriculum_list')



class AddTeacher2DisciplineOnTerm(ObjectDetailView):
    template_name = 'Curriculum/detail/addTeacher2DisciplineOnTerm.html'
    model = Curriculum
    context_object_name = 'curriculum'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        categories = Category.objects.filter(curriculum=self.object)

        study_cycles = []
        for category in categories:
            study_cycles += StudyCycle.objects.filter(categories=category)

        study_cycle_disciplines = []
        modules = []
        for study_cycle in study_cycles:
            study_cycle_disciplines += study_cycle.disciplines.all()
            modules += study_cycle.modules.all()

        modules_disciplines = []
        for module in modules:
            modules_disciplines += module.disciplines.all()

        context['categories'] = categories
        context['study_cycles'] = study_cycles
        context['modules'] = modules
        context['study_cycle_disciplines'] = study_cycle_disciplines
        context['modules_disciplines'] = modules_disciplines
        context['clock_cells'] = ClockCell.objects.filter(curriculum=self.object)

        return context



