import json
from collections import defaultdict
from platform import release

import pandas as pd  # Import pandas for Excel processing
from django.contrib import messages
from django.core.exceptions import FieldError
from django.http import HttpResponseForbidden, HttpRequest
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import TemplateView

from Academhub.generic import ObjectTableView, ObjectCreateView, ImportViewMixin, ObjectTemplateView, ObjectDetailView
from Academhub.models import ClockCell, Category, StudyCycle, Discipline, CustomUser, ReleaseFromCurriculum, Button
from Academhub.models.models import Specialty, Qualification, GroupStudents, Curriculum
from Academhub.utils import getpermission, getpattern
from .filters import CurriculumQualificationsFilter, ReleaseFromCurriculumFilter
from .forms.EditableCurriculumForm import EditableCurriculumForm
from .forms.GetPlxForm import GetPlxForm
from .models.curriculum_datail_objects import *
from .tables import CurriculumTable, ReleaseFromCurriculumTable

__all__ = (
    'CurriculumTableView',
    'CurricullumAddView',
    'CurriculumDeleteView',
    'CurriculumEditableFormView',
    'CurriculumPreviewView',
    'CompleteSetCurriculum',
    'SetAttestationPeriodView',
    'ReleaseFromCurriculumDetailView',
    'ReleaseFromCurriculumCreateView',
    'ReleaseFromCurriculumView',
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
        
class CurriculumDeleteView(DeleteView):
    model = Curriculum
    success_url = reverse_lazy('curriculum_list')  # URL для перенаправления после удаления
    template_name = 'confirmation_delete.html'  # Опционально, если нужно подтверждение

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Проверка данных (например, через POST-параметры)
        if (request.POST.get('year') == str(self.object.admission_year) and
            request.POST.get('qualification') == self.object.qualification):
            return super().delete(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Неверные данные для удаления!")


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
            disciplines = json.loads(uploaded_data_json).get('disciplines', [])
            context['discipline_indices'] = range(len(disciplines))

        context['semester_list'] = ["1", "2", "3", "4", "5", "6", "7", "8"]
        return context

    def post(self, request, *args, **kwargs):
        uploaded_data_json = request.session.get('uploaded_data')
        form = EditableCurriculumForm(uploaded_data_json)
        # if self.form_valid(form):
        #     return redirect('curriculum_list')
        # else:
        #     context = self.get_context_data(**kwargs)
        #     context['editable_form'] = form
        # context = self.get_context_data(**kwargs)
        # context['editable_form'] = form
        # return self.render_to_response(context)

        uploaded_data_json = self.request.session.get('uploaded_data')
        if uploaded_data_json:
            data = json.loads(uploaded_data_json)
            print(f"Размер данных: {len(uploaded_data_json)} байт")  # Для локальной отладки
            if len(uploaded_data_json) > 1024 * 1024:  # Например, лимит 1 МБ
                messages.error(self.request, "Слишком большой объем данных")
                return redirect('curriculum_list')
        form.save()
        messages.success(self.request, "Успешное сохранение учебного плана")
        return redirect('curriculum_list')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Успешное сохранение учебного плана"
        )
        return redirect('curriculum_list')


class CurriculumPreviewView(ObjectDetailView):
    model = Curriculum
    template_name = 'Curriculum/detail/preview_form.html'
    context_object_name = 'curriculum_data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curriculum = self.object
        disciplines_data = []
        unique_disciplines: set = set()

        for clock_cell in ClockCell.objects.filter(curriculum=curriculum.id, module__isnull=True):
            if clock_cell.discipline is not None:
                tmp = Discipline.objects.filter(id=clock_cell.discipline.id).get().to_dict()
                if clock_cell.discipline.name not in unique_disciplines:
                    unique_disciplines.add(clock_cell.discipline.name)
                    tmp["semesters"] = defaultdict(int)
                    disciplines_data.append(tmp)
                if clock_cell.code_of_type_work == 'Итого часов':
                    for i, disc in enumerate(disciplines_data):
                        if disc.get("name") == clock_cell.discipline.name:
                            disciplines_data[i]["semesters"][clock_cell.term] = clock_cell.count_of_clocks

        context.update({
            'disciplines_data': disciplines_data,
            'semester_list': list(range(1, 9)),
        })
        return context


class CompleteSetCurriculum(ObjectTemplateView):
    template_name = 'Curriculum/complete_set/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["specialties"] = Specialty.objects.all()

        return context


# Placeholder View for setting attestation periods
class SetAttestationPeriodView(ObjectTemplateView):
    template_name = 'Curriculum/attestation_period/set_period.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["specialties"] = Specialty.objects.all()


        return context



class CurriculumDetail(ObjectDetailView):
    """
    Этот класс нужен для вывода данных по конкретному учебному плану.
    На данный момент просто собирает все данные по уч плану, никак не используя их.
    Потом будет выводить табличку полноценную.

    Сейчас показывает тольк дисциплины и семестры в которых она идёт.
    """
    template_name = 'Curriculum/detail/curriculum_detail.html'
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

        all_clock_cells = ClockCell.objects.filter(curriculum=self.object)

        table_disciplines = []
        for discipline in study_cycle_disciplines:
            discipline_view = DisciplineView(
                discipline.id,
                discipline.code,
                discipline.name
            )
            for clock_cell in all_clock_cells:
                if clock_cell.discipline:
                    if f"{discipline.code}.{discipline.name}" == f"{clock_cell.discipline.code}.{clock_cell.discipline.name}":
                        if len(list(filter(lambda x: x.course == clock_cell.course and x.term == clock_cell.term, discipline_view.when_going))) == 0:
                            discipline_view.when_going.append(
                                CourseAndTermView(
                                    clock_cell.course,
                                    clock_cell.term
                                )
                            )

            table_disciplines.append(discipline_view)


        for discipline in modules_disciplines:
            discipline_view = DisciplineView(
                discipline.id,
                discipline.code,
                discipline.name
            )
            for clock_cell in all_clock_cells:
                if clock_cell.discipline:
                    if f"{discipline.code}.{discipline.name}" == f"{clock_cell.discipline.code}.{clock_cell.discipline.name}":
                        if len(list(filter(lambda x: x.course == clock_cell.course and x.term == clock_cell.term, discipline_view.when_going))) == 0:
                            discipline_view.when_going.append(
                                CourseAndTermView(
                                    clock_cell.course,
                                    clock_cell.term
                                )
                            )

            table_disciplines.append(discipline_view)

        context['categories'] = categories
        context['study_cycles'] = study_cycles
        context['modules'] = modules
        context['study_cycle_disciplines'] = study_cycle_disciplines
        context['modules_disciplines'] = modules_disciplines

        context['clock_cells'] = all_clock_cells
        context['table_disciplines'] = table_disciplines

        return context


class ReleaseFromCurriculumView(ObjectTableView):
    table_class = ReleaseFromCurriculumTable
    filterset_class = ReleaseFromCurriculumFilter
    queryset = ReleaseFromCurriculum.objects.all()

    permission_required = getpermission('Curriculum', 'view_release_from_curriculum')

    buttons = [
        Button(
            id='add',
            name='Добавить',
            link_name=getpattern('ReleaseFromCurriculum', 'add'),
            permission=getpermission('Contingent', 'create_group_student'),
        )
    ]



class ReleaseFromCurriculumCreateView(ObjectTemplateView):
    template_name = 'Curriculum/create/create_release.html'
    model = ReleaseFromCurriculum

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["qualifications"] = Qualification.objects.all()

        return context


class ReleaseFromCurriculumDetailView(ObjectTemplateView):
    template_name = 'Curriculum/detail/release_detail.html'
    model = ReleaseFromCurriculum

    permission_required = getpermission('ReleaseFromCurriculum', 'view_release_from_curriculum')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = context['pk']
        release = ReleaseFromCurriculum.objects.get(pk=pk)
        curriculum = release.curriculum

        context["release_id"] = release.id
        context["release_course"] = release.course
        context["release_study_year"] = release.study_year
        context["curriculum_id"] = curriculum.id
        context["curriculum_speciality"] = curriculum.qualification.specialty.code

        return context
