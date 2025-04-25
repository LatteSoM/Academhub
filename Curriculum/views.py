import json
from collections import defaultdict

import pandas as pd  # Import pandas for Excel processing
from django.contrib import messages
from django.core.exceptions import FieldError
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import TemplateView

from Academhub.generic import ObjectTableView, ObjectCreateView, ImportViewMixin, ObjectTemplateView, ObjectDetailView
from Academhub.models import ClockCell, Category, StudyCycle, Discipline, CustomUser
from Academhub.models.models import Specialty, Qualification, GroupStudents, Curriculum
from .filters import CurriculumQualificationsFilter
from .forms.EditableCurriculumForm import EditableCurriculumForm
from .forms.GetPlxForm import GetPlxForm
from .models.curriculum_datail_objects import *
from .tables import CurriculumTable

__all__ = (
    'CurriculumTableView',
    'CurricullumAddView',
    'CurriculumDeleteView',
    'CurriculumEditableFormView',
    'CurriculumPreviewView',
    'CompleteSetCurriculum', # Add the new view to __all__
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


# Placeholder View for setting attestation periods
class SetAttestationPeriodView(ObjectTemplateView):
    template_name = 'Curriculum/attestation_period/set_period.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # --- Get selected IDs from query parameters ---
        selected_specialty_id = request.GET.get('specialty')
        selected_study_plan_id = request.GET.get('study_plan')
        selected_course_id = request.GET.get('course')
        selected_group_ids_str = request.GET.get('groups', '')
        selected_term = request.GET.get('term', '1') # Default to term 1 if not provided

        selected_group_ids = []
        if selected_group_ids_str:
            try:
                # Ensure IDs are integers if your model uses integer PKs
                selected_group_ids = [int(gid) for gid in selected_group_ids_str.split(',') if gid.isdigit()]
            except ValueError:
                messages.warning(request, "Неверный формат ID групп.")
                selected_group_ids = []

        # --- Pass selected IDs to context ---
        # --- Bundle selected IDs for JS ---
        initial_selections = {
            'specialty_id': int(selected_specialty_id) if selected_specialty_id and selected_specialty_id.isdigit() else None,
            'plan_id': int(selected_study_plan_id) if selected_study_plan_id and selected_study_plan_id.isdigit() else None,
            'course_id': int(selected_course_id) if selected_course_id and selected_course_id.isdigit() else None,
            'group_ids': selected_group_ids,
            'term': int(selected_term) if selected_term and selected_term.isdigit() else 1
        }
        context['initial_selections'] = initial_selections

        # --- Fetch data for dropdowns/checkboxes based on selections ---
        # We still need the individual IDs for server-side filtering during initial load
        selected_specialty_id_int = initial_selections['specialty_id']
        selected_study_plan_id_int = initial_selections['plan_id']
        selected_course_id_int = initial_selections['course_id']
        selected_term_int = initial_selections['term']
        # selected_group_ids remains the same list

        context["specialties"] = Specialty.objects.all()
        context["study_plans"] = Curriculum.objects.none() # Default to empty
        context["courses"] = [] # Default to empty
        context["groups"] = GroupStudents.objects.none() # Default to empty
        context["disciplines"] = [] # Default to empty

        # Filter Curriculums (Study Plans) via Qualification linked to Specialty
        if selected_specialty_id_int:
            try:
                # Assuming Qualification has a ForeignKey 'specialty' to Specialty model
                qualifications = Qualification.objects.filter(specialty_id=selected_specialty_id_int)
                context["study_plans"] = Curriculum.objects.filter(qualification__in=qualifications)
            except Qualification.DoesNotExist:
                 messages.warning(request, "Квалификации для выбранной специальности не найдены.")
                 context["study_plans"] = Curriculum.objects.none()
            except FieldError: # Catch if the assumed 'specialty_id' on Qualification is wrong
                 messages.error(request, "Ошибка связи между Специальностью и Квалификацией. Проверьте модели.")
                 context["study_plans"] = Curriculum.objects.none()

        # Fetch Courses and Groups based on selected Curriculum (Study Plan)
        if selected_study_plan_id_int:
            # Assuming StudyPlan has a relation to get courses (e.g., through ClockCell or similar)
            # This logic might need adjustment based on your actual models
            try:
                curriculum_obj = Curriculum.objects.get(id=selected_study_plan_id_int) # Use curriculum_obj consistently
                # Example: Get distinct courses from ClockCells related to this curriculum
                courses_qs = ClockCell.objects.filter(curriculum=curriculum_obj).values_list('course', flat=True).distinct().order_by('course')
                context["courses"] = list(courses_qs)

                if selected_course_id_int:
                     # Filter GroupStudents by Qualification from Curriculum and selected course
                     context["groups"] = GroupStudents.objects.filter(
                         qualification=curriculum_obj.qualification, # Use qualification from curriculum_obj
                         current_course=selected_course_id_int # Use current_course field
                     ).order_by('full_name') # Order by full_name

            except Curriculum.DoesNotExist:
                 messages.error(request, "Выбранный учебный план не найден.")


        # --- Fetch Disciplines based on selected groups and term ---
        # !!! This logic heavily depends on your model structure !!!
        # Example: Find disciplines linked via ClockCell for the selected curriculum, course, term,
        # and potentially filter further if disciplines are group-specific.
        # This is a simplified example assuming disciplines are tied to curriculum/course/term.
        if selected_study_plan_id_int and selected_course_id_int and selected_term_int:
             try:
                 # Use the already fetched curriculum_obj if available, otherwise fetch Curriculum
                 curriculum_obj = Curriculum.objects.get(id=selected_study_plan_id_int)
                 discipline_ids = ClockCell.objects.filter(
                     curriculum=curriculum_obj, # Use curriculum_obj
                     course=selected_course_id_int,
                     term=selected_term_int,
                     discipline__isnull=False
                 ).values_list('discipline_id', flat=True).distinct()

                 # Fetch actual Discipline objects
                 # You might want to add attestation dates here if stored on Discipline model
                 # or fetch them from another related model
                 context['disciplines'] = Discipline.objects.filter(id__in=discipline_ids).order_by('name')

                 # If disciplines are specific to groups, you'd need further filtering based on selected_group_ids
                 # This requires knowing how Disciplines/ClockCells relate to StudyGroups

             except Curriculum.DoesNotExist:
                 pass # Already handled above

        # Add a message if the page is loaded without full selections needed for disciplines
        if not context['disciplines'] and (selected_study_plan_id_int or selected_course_id_int or selected_term_int):
             messages.info(request, "Выберите учебный план, курс, семестр и группы для отображения дисциплин.")
        elif not selected_study_plan_id_int:
             messages.info(request, "Выберите специальность и учебный план.")


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

# def import_teachers_excel_view(request):
#     if request.method == 'POST':
#         excel_file = request.FILES.get('excel_file')
#         if not excel_file:
#             messages.error(request, "Не был выбран файл Excel.")
#             referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
#             return redirect(referer_url)
#
#         if not excel_file.name.endswith(('.xls', '.xlsx')):
#              messages.error(request, "Неверный формат файла. Пожалуйста, загрузите файл Excel (.xls или .xlsx).")
#              referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
#              return redirect(referer_url)
#
#         created_count = 0
#         updated_count = 0
#         skipped_count = 0
#         deactivated_count = 0
#         errors = []
#         excel_emails = set()
#
#         try:
#             df = pd.read_excel(excel_file, sheet_name=0)
#             required_columns = ['ФИО','email', 'ЦМК']
#
#             if not all(col in df.columns for col in required_columns):
#                 missing_cols = [col for col in required_columns if col not in df.columns]
#                 messages.error(request, f"В файле отсутствуют необходимые столбцы: {', '.join(missing_cols)}")
#                 referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
#                 return redirect(referer_url)
#
#             for index, row in df.iterrows():
#                 try:
#                     full_name_raw = row.get('ФИО')
#                     email_raw = row.get('email')
#                     cmk_raw = row.get('ЦМК')
#
#                     full_name = str(full_name_raw).strip() if pd.notna(full_name_raw) else None
#                     email = str(email_raw).strip() if pd.notna(email_raw) else None
#                     cmk = str(cmk_raw).strip() if pd.notna(cmk_raw) else None
#
#                     if not all([full_name, email]):
#                         errors.append(f"Строка {index + 2}: Отсутствуют обязательные данные (ФИО или email).")
#                         skipped_count += 1
#                         continue
#
#                     name_parts = full_name.split()
#                     last_name = name_parts[0] if len(name_parts) > 0 else ''
#                     first_name = name_parts[1] if len(name_parts) > 1 else ''
#                     # middle_name = ' '.join(name_parts[2:]) if len(name_parts) > 2 else '' # Not used currently based on user edits
#
#                     if not last_name or not first_name:
#                          errors.append(f"Строка {index + 2}: Не удалось разобрать ФИО '{full_name}'. Ожидается как минимум Фамилия и Имя.")
#                          skipped_count += 1
#                          continue
#
#
#                     user_defaults = {
#                         'full_name': full_name,
#                         'is_teacher': True,
#                         'is_active': True
#                     }
#
#                     #TODO Придумать где хранить связи с ЦМК (user_defaults['cmk'] = cmk)
#
#                     user, created = CustomUser.objects.update_or_create(
#                         email=email,
#                         defaults=user_defaults
#                     )
#
#                     if created:
#                         email_part = str(email.split("@")[0])
#                         against_overkill_par = "123456789"
#                         user.set_password(email_part + against_overkill_par)
#                         user.save()
#                         created_count += 1
#                     else:
#                         updated_count += 1
#
#                     excel_emails.add(email)
#
#                 except Exception as e:
#                     errors.append(f"Строка {index + 2}: Ошибка обработки - {e}")
#                     skipped_count += 1
#
#             existing_teacher_emails = set(CustomUser.objects.filter(is_teacher=True, is_active=True).values_list('email', flat=True))
#             emails_to_deactivate = existing_teacher_emails - excel_emails
#
#             if emails_to_deactivate:
#                 users_to_deactivate = CustomUser.objects.filter(email__in=emails_to_deactivate, is_teacher=True)
#                 for user in users_to_deactivate:
#                     user.is_active = False
#                     user.save()
#                     deactivated_count += 1
#
#         except Exception as e:
#             messages.error(request, f"Произошла ошибка при обработке файла: {e}")
#             referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
#             return redirect(referer_url)
#
#         final_message_parts = []
#         if created_count > 0:
#             final_message_parts.append(f"Создано: {created_count}")
#         if updated_count > 0:
#             final_message_parts.append(f"Обновлено/Подтверждено: {updated_count}")
#         if deactivated_count > 0:
#             final_message_parts.append(f"Деактивировано (не найдены в файле): {deactivated_count}")
#         if skipped_count > 0:
#             final_message_parts.append(f"Пропущено строк из-за ошибок: {skipped_count}")
#
#         if final_message_parts:
#              final_message = "Импорт завершен. " + ", ".join(final_message_parts) + "."
#              if created_count > 0 or updated_count > 0 or deactivated_count > 0:
#                  messages.success(request, final_message)
#              else:
#                  messages.warning(request, final_message)
#         else:
#              messages.info(request, "Файл обработан, но не найдено данных для создания, обновления или деактивации.")
#
#         if errors:
#             messages.warning(request, "Обнаружены следующие ошибки в строках:")
#             for error in errors:
#                 messages.error(request, error)
#
#         referer_url = request.META.get('HTTP_REFERER', reverse('curriculum_list'))
#         return redirect(referer_url)
#
#     else:
#         messages.error(request, "Недопустимый метод запроса.")
#         return redirect(reverse('curriculum_list'))
