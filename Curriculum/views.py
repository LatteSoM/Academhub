import json
from collections import defaultdict

from django.http import HttpResponseForbidden
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
# from parser_for_plx import RUP_parser
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.views.generic import DeleteView
from unicodedata import category
import pandas as pd # Import pandas for Excel processing

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from Academhub.models import Curriculum, CustomUser # Add CustomUser
from django.urls import reverse_lazy

from Academhub.models.models import Module, Specialty
from .models.curriculum_datail_objects import *
from Academhub.generic import ObjectTableView, ObjectCreateView, ImportViewMixin, ObjectTemplateView, ObjectDetailView
from Academhub.models import Curriculum, ClockCell, Category, StudyCycle, Discipline, CustomUser
from .filters import CurriculumQualificationsFilter
from .forms.GetPlxForm import GetPlxForm
from .forms.EditableCurriculumForm import EditableCurriculumForm
from .tables import CurriculumTable

__all__ = (
    'CurriculumTableView',
    'CurriculumAddView',
    'CurriculumDeleteView',
    'CurriculumEditableFormView',
    'CurriculumPreviewView',
    'CompleteSetCurriculum',
    'import_teachers_excel_view', # Add the new view to __all__
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


class CurriculumAddView(ObjectCreateView):
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
        form = EditableCurriculumForm(uploaded_data_json, data=request.POST)
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

##### Легаси обработчики - не работают после изменения TeachersForDisciplineAndCurriculum в models
#
# class AddTeacher2DisciplineOnTerm(ObjectTemplateView):
#     """
#     Этот класс нужен для добавления преподавателям возможность вести дисциплину в конретномсеместре
#     """
#     template_name = 'Curriculum/create/addTeacher2DisciplineOnTerm.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         curriculum = Curriculum.objects.get(id=context["pk"])
#         discipline = Discipline.objects.get(id=context["discipline_id"])
#         teachers = CustomUser.objects.filter(is_teacher=True)
#         teachers_of_discipline = TeachersForDisciplineAndCurriculum.objects.filter(
#             curriculum=curriculum,
#             course=context['course_number'],
#             term=context['term_number'],
#             discipline=discipline
#         )
#
#         techers_who_not_lead_discipline = []
#
#         for teacher in teachers:
#             lead = False
#             for teacher_of_discipline in teachers_of_discipline:
#                 if teacher.id == teacher_of_discipline.teacher.id:
#                     lead = True
#                     break
#
#             if not lead:
#                 techers_who_not_lead_discipline.append(teacher)
#
#         context['discipline'] = discipline
#         context['curriculum'] = curriculum
#         context['teachers_of_discipline'] = teachers_of_discipline
#         context['teachers'] = techers_who_not_lead_discipline
#
#
#         return context
#
#
# class AddTeacherToDiscipline(View):
#     """
#     Класс который обрабатывает запрос на добавление из AddTeacher2DisciplineOnTerm
#     """
#     def post(self, request, pk, discipline_id, course_number, term_number, teacher_id):
#         discipline = Discipline.objects.get(id=discipline_id)
#         teacher = CustomUser.objects.get(id=teacher_id)
#         curriculum = Curriculum.objects.get(id=pk)
#
#         new_teacher_for_discipline = TeachersForDisciplineAndCurriculum(
#             teacher=teacher,
#             course=course_number,
#             term=term_number,
#             discipline=discipline,
#             curriculum=curriculum
#         )
#
#         new_teacher_for_discipline.save()
#         messages.success(request, f'Преподаватель {teacher} успешно добавлен')
#         return redirect('curriculum_add_teacher', pk=pk, discipline_id=discipline_id, course_number=course_number, term_number=term_number)
#
#
# class RemoveTeacherFromDiscipline(View):
#     """
#     Класс обрабатывает запрос на удаление из класса AddTeacher2DisciplineOnTerm
#     """
#     def post(self, request, pk, discipline_id, course_number, term_number, teacher_id):
#         discipline = Discipline.objects.get(id=discipline_id)
#         teacher = CustomUser.objects.get(id=teacher_id)
#         curriculum = Curriculum.objects.get(id=pk)
#
#         teacher_discipline = TeachersForDisciplineAndCurriculum.objects.get(
#             teacher=teacher,
#             course=course_number,
#             term=term_number,
#             discipline=discipline,
#             curriculum=curriculum
#         )
#         teacher_discipline.delete()
#         messages.success(request, f'Преподаватель {teacher.full_name} больше не может вести дисциплину {discipline.name}')
#         return redirect('curriculum_add_teacher', pk=pk, discipline_id=discipline_id, course_number=course_number, term_number=term_number)



def import_teachers_excel_view(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, "Не был выбран файл Excel.")
            referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
            return redirect(referer_url)

        if not excel_file.name.endswith(('.xls', '.xlsx')):
             messages.error(request, "Неверный формат файла. Пожалуйста, загрузите файл Excel (.xls или .xlsx).")
             referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
             return redirect(referer_url)

        try:
            df = pd.read_excel(excel_file, sheet_name=0)

            required_columns = ['ФИО','email', 'ЦМК']

            if not all(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                messages.error(request, f"В файле отсутствуют необходимые столбцы: {', '.join(missing_cols)}")
                referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
                return redirect(referer_url)

            created_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    full_name_raw = row.get('ФИО')
                    email_raw = row.get('email')
                    cmk_raw = row.get('ЦМК')

                    full_name = str(full_name_raw).strip() if pd.notna(full_name_raw) else None
                    email = str(email_raw).strip() if pd.notna(email_raw) else None
                    cmc = str(cmk_raw).strip() if pd.notna(cmk_raw) else None

                    if not all([full_name, email]):
                        errors.append(f"Строка {index + 2}: Отсутствуют обязательные данные (ФИО или email).")
                        skipped_count += 1
                        continue

                    name_parts = full_name.split()
                    last_name = name_parts[0] if len(name_parts) > 0 else ''
                    first_name = name_parts[1] if len(name_parts) > 1 else ''
                    middle_name = ' '.join(name_parts[2:]) if len(name_parts) > 2 else '' # Handle multiple middle names/parts

                    if not last_name or not first_name:
                         errors.append(f"Строка {index + 2}: Не удалось разобрать ФИО '{full_name}'. Ожидается как минимум Фамилия и Имя.")
                         skipped_count += 1
                         continue

                    user_defaults = {
                        'full_name': full_name,
                        'is_teacher': True,
                    }

                    #TODO Придумать где хранить связи с ЦМК
                    user, created = CustomUser.objects.update_or_create(
                        email=email,
                        defaults=user_defaults,
                        cmc=cmc
                    )

                    if created:
                        email_part = str(email.split("@")[0])
                        against_overkill_par = "123456789"
                        user.set_password(email_part + against_overkill_par)
                        user.save()
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Строка {index + 2}: Ошибка обработки - {e}")
                    skipped_count += 1

            # --- feedback to the user ---
            if created_count > 0 or updated_count > 0:
                 success_msg = f"Импорт завершен. Создано: {created_count}, Обновлено: {updated_count}."
                 if skipped_count > 0:
                     success_msg += f" Пропущено из-за ошибок: {skipped_count}."
                 messages.success(request, success_msg)
            else:
                 messages.warning(request, f"Импорт завершен. Нет созданных или обновленных записей. Пропущено из-за ошибок: {skipped_count}.")

            if errors:
                for error in errors:
                    messages.error(request, error)

        except Exception as e:
            messages.error(request, f"Произошла ошибка при обработке файла: {e}")


        referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
        return redirect(referer_url)

    else:
        messages.error(request, "Недопустимый метод запроса.")
        return redirect(reverse('curriculum_list'))


