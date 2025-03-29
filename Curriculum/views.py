import json

from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
# from parser_for_plx import RUP_parser
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, DetailView

from Academhub.models.models import TeacherDicsciplineCurriculum
from .models.curriculum_datail_objects import *
from Academhub.generic import ObjectTableView, ObjectCreateView, ImportViewMixin, ObjectTemplateView, ObjectDetailView
from Academhub.models import Curriculum, ClockCell, Category, StudyCycle, Discipline, CustomUser
from .filters import CurriculumQualificationsFilter
from .forms.GetPlxForm import GetPlxForm
from .forms.EditableCurriculumForm import EditableCurriculumForm
from .tables import CurriculumTable

__all__ = (
    'CurriculumTableView',
    'CurricullumAddView',
    'CurriculumEditableFormView',
    'CurriculumDetail',
    'AddTeacher2DisciplineOnTerm',
    'RemoveTeacherFromDiscipline',
    'AddTeacherToDiscipline'
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



class AddTeacher2DisciplineOnTerm(ObjectTemplateView):
    """
    Этот класс нужен для добавления преподавателям возможность вести дисциплину в конретномсеместре
    """
    template_name = 'Curriculum/create/addTeacher2DisciplineOnTerm.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        curriculum = Curriculum.objects.get(id=context["pk"])
        discipline = Discipline.objects.get(id=context["discipline_id"])
        teachers = CustomUser.objects.filter(is_teacher=True)
        teachers_of_discipline = TeacherDicsciplineCurriculum.objects.filter(
            curriculum=curriculum,
            course=context['course_number'],
            term=context['term_number'],
            discipline=discipline
        )

        techers_who_not_lead_discipline = []

        for teacher in teachers:
            lead = False
            for teacher_of_discipline in teachers_of_discipline:
                if teacher.id == teacher_of_discipline.teacher.id:
                    lead = True
                    break
            
            if not lead:
                techers_who_not_lead_discipline.append(teacher)

        context['discipline'] = discipline
        context['curriculum'] = curriculum
        context['teachers_of_discipline'] = teachers_of_discipline
        context['teachers'] = techers_who_not_lead_discipline
        

        return context
        

class AddTeacherToDiscipline(View):
    """
    Класс который обрабатывает запрос на добавление из AddTeacher2DisciplineOnTerm
    """
    def post(self, request, pk, discipline_id, course_number, term_number, teacher_id):
        discipline = Discipline.objects.get(id=discipline_id)
        teacher = CustomUser.objects.get(id=teacher_id)
        curriculum = Curriculum.objects.get(id=pk)

        new_teacher_for_discipline = TeacherDicsciplineCurriculum(
            teacher=teacher,
            course=course_number,
            term=term_number,
            discipline=discipline,
            curriculum=curriculum
        )

        new_teacher_for_discipline.save()
        messages.success(request, f'Преподаватель {teacher} успешно добавлен')
        return redirect('curriculum_add_teacher', pk=pk, discipline_id=discipline_id, course_number=course_number, term_number=term_number)


class RemoveTeacherFromDiscipline(View):
    """
    Класс обрабатывает запрос на удаление из класса AddTeacher2DisciplineOnTerm
    """
    def post(self, request, pk, discipline_id, course_number, term_number, teacher_id):
        discipline = Discipline.objects.get(id=discipline_id)
        teacher = CustomUser.objects.get(id=teacher_id)
        curriculum = Curriculum.objects.get(id=pk)

        teacher_discipline = TeacherDicsciplineCurriculum.objects.get(
            teacher=teacher,
            course=course_number,
            term=term_number,
            discipline=discipline,
            curriculum=curriculum
        )
        teacher_discipline.delete()
        messages.success(request, f'Преподаватель {teacher.full_name} больше не может вести дисциплину {discipline.name}')
        return redirect('curriculum_add_teacher', pk=pk, discipline_id=discipline_id, course_number=course_number, term_number=term_number)

    

