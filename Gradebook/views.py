import datetime
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

import matplotlib
from django.urls import reverse
from django.views import View

matplotlib.use('Agg')  # Set backend to Agg
import matplotlib.pyplot as plt
from io import BytesIO

import numpy as np
from django.db.models import Prefetch, Q, Func, F
from openpyxl.styles import PatternFill, Font, Alignment, Side, Border
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
from unidecode import unidecode

from Academhub import settings
from django.db.models.functions import Trim
from Academhub.modules.documentGenPars import GradebookDocumentGenerator
from Gradebook.forms import *
from Gradebook.forms import GenerateGradebookForm, GetStatisticksGradebookForm, GetDiplomTypeGradebookForm
from Gradebook.tables import *
from Gradebook.filters import *
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from Gradebook.mixins import GradeBookMixin
from Gradebook.tables import TeacherGradeBookTable
from Academhub.utils import getpermission, getpattern
from Gradebook.filters import GradeBookTeachersFilter
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import permission_required
from Academhub.models import GradebookStudents, Gradebook, CustomUser, SubTable, Button, Discipline, Student, \
    GroupStudents, ClockCell, Curriculum
from Academhub.generic import BulkUpdateView, ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView, \
    ObjectTemplateView


#
# Create your views here.
#

__all__ = (
    'download_report',
    "export_diplom_types",
    'GradebookTableView',
    'GradebookClosedList',
    'GradebookDetailView',
    'GradebookCreateView',
    'GradebookUpdateView',
    'check_and_open_gradebook',
    'TeachersGradeBookTableView',
    'GradebookStudentBulkUpdateView',
)


def get_last_grade(student, discipline, semester):
    """
    Возвращает последнюю оценку студента по дисциплине с учетом всех типов ведомостей.
    Порядок проверки: комиссия → пересдача → первичная сдача
    """
    gradebook_types = ["Комиссия", "Пересдача", "Первичная сдача"]

    for gradebook_type in gradebook_types:
        grade = GradebookStudents.objects.filter(
            student=student,
            gradebook__discipline=discipline,
            gradebook__semester_number=semester,
            gradebook__type_of_grade_book=gradebook_type
        ).order_by('-gradebook__date_of_closing').first()

        if grade:
            return grade.grade
    return None


def check_students_for_academic_debts(group, semester):
    """
    Проверяет студентов группы на наличие академических задолженностей
    """
    students = Student.objects.filter(
        group=group,
        is_in_academ=False,
        is_expelled=False
    ).select_related('group')

    disciplines = set()
    grade_books = Gradebook.objects.filter(semester_number=semester, group=group)
    for gb in grade_books:
        disciplines.add(gb.discipline)

    for student in students:
        has_debt = False

        for discipline in disciplines:
            last_grade = get_last_grade(student, discipline, semester)

            if last_grade in ["2", "Неявка"]:
                has_debt = True
                break  # Достаточно одной двойки для задолженности

        # Обновляем статус студента
        if student.academic_debts != has_debt:
            student.academic_debts = has_debt
            student.save()

        print(f"Студент {student}: {'есть долги' if has_debt else 'нет долгов'}")

class GradebookStudentBulkUpdateView(BulkUpdateView):
    model = GradebookStudents
    form_class = GradebookStudentsForm
    template_name = 'Gradebook/create/grade_book_students.html'

    def dispatch(self, request, *args, **kwargs):
        self.gradebook_pk = self.kwargs.get('pk', None)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(gradebook__pk = self.gradebook_pk)

    def get(self, request, *args, **kwargs):
        self.gradebook = get_object_or_404(Gradebook, pk=self.gradebook_pk)
        if self.gradebook.status not in ["Открыта", "Заполнена"]:
            messages.error(
                request,
                "Заполнить/изменить можно только открытую или уже заполненную ведомость"
            )
            logger.warning(
                f"Attempt to access gradebook {self.gradebook_pk} with status {self.gradebook.status}"
            )
            return redirect(reverse('gradebook_detail', kwargs={'pk': self.gradebook_pk}))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gradebook'] = self.gradebook
        return context

    def save_form(self, request):
        form = super().save_form(request)

        if form.is_valid():
            gradebook = get_object_or_404(
                Gradebook,
                pk=self.gradebook_pk
            )

            check_students_for_academic_debts(gradebook.group, gradebook.semester_number)

            gradebook.status = Gradebook.STATUS_CHOICE[2][1]
            gradebook.date_of_filling = timezone.now()
            gradebook.save()

        return form

    def post(self, request, *args, **kwargs):
        formset = self.save_form(request)

        if formset.is_valid():
            user = get_object_or_404(CustomUser, pk=self.request.user.pk)

            if user.is_teacher:
                response = redirect('gradebookteacher_list')
            else:
                response = redirect('gradebook_list')
            response['Location'] += '?is_filled=true'
            return response
        return super().post(request, *args, **kwargs)


class GradebookGenerateView(ObjectTemplateView):
    """Отдельный класс для обработки генерации"""
    template_name = 'Gradebook/inc/generate_form.html'

    def get(self, request):
        form = GenerateGradebookForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GenerateGradebookForm(request.POST)  # Создаем экземпляр формы

        if form.is_valid():  # Проверяем валидность ФОРМЫ, а не представления
            try:
                semester = form.cleaned_data['semester']  # Данные берем из формы
                gradebook_type = form.cleaned_data['type_of_gradebook']
                result = perform_generation(semester, gradebook_type)

                if result['generated'] > 0 and result['errors'] == 0:
                    messages.success(request,
                                     f"Успешно сгенерировано {result['generated']} ведомостей для {semester} семестра! С типом {result['grade_book_type']}")
                elif result['generated'] > 0:
                    messages.warning(request,
                                     f"Сгенерировано {result['generated']} ведомостей для {semester} семестра. С типом {result['grade_book_type']} "
                                     f"Ошибок: {result['errors']}")
                else:
                    messages.error(request,
                                   "Не удалось сгенерировать ни одной ведомости!")

                return redirect('gradebook_list')

            except Exception as e:
                messages.error(request, f"Ошибка генерации: {str(e)}")
                return redirect('gradebook_list')

        # Если форма невалидна, показываем ее с ошибками
        return render(request, self.template_name, {'form': form})


def is_pm_discipline(discipline):
    """Проверяет, является ли дисциплина ПМ по формату кода ПМ.XX.XXX"""
    code = str(discipline.code).strip().upper()
    return re.match(r'^П[МM]\.\d{2}\.', code, re.IGNORECASE) is not None


def extract_pm_number(pm_code):
    """Извлекает номер из кода ПМ (например, '01' из 'ПМ.01.ЭК')"""
    normalized_code = str(pm_code).upper().replace("M", "М")
    print(f"Normalized code: {normalized_code}")  # Отладочный вывод

    match = re.match(r"^ПМ\.(\d{2})\..*", normalized_code)
    if match:
        print(f"Match groups: {match.groups()}")  # Проверка групп
    return match.group(1) if match else None


def get_required_prefixes(pm_number):
    """Генерирует префиксы для проверяемых дисциплин"""
    return [
        f'МДК.{pm_number}.',
        f'УП.{pm_number}.',
        f'ПП.{pm_number}.'
    ]


class Strip(Func):
    function = 'TRIM'
    template = '%(function)s(%(expressions)s)'


def has_required_grades(student, pm_discipline):
    pm_number = extract_pm_number(pm_discipline.code)
    if not pm_number:
        return False

    prefixes = get_required_prefixes(pm_number)

    # Получаем все подходящие дисциплины (с очисткой пробелов)
    disciplines = Discipline.objects.annotate(
        clean_code=Strip('code')
    ).filter(
        Q(clean_code__startswith=prefixes[0]) |
        Q(clean_code__startswith=prefixes[1]) |
        Q(clean_code__startswith=prefixes[2])
    )

    return GradebookStudents.objects.filter(
        student=student,
        gradebook__discipline__in=disciplines,
        grade__in=['5', '4', '3']
    ).exists()


def update_grade_book_contingent(gradebook, students):
    try:
        GradebookStudents.objects.filter(gradebook=gradebook).delete()

        if is_pm_discipline(gradebook.discipline):
            # Фильтрация студентов с выполненными требованиями
            print(f"{gradebook.discipline} is PM")
            allowed_students = [
                s for s in students
                if has_required_grades(s, gradebook.discipline)
            ]

        else:
            allowed_students = students

        for student in allowed_students:
            GradebookStudents.objects.create(
                student=student,
                gradebook=gradebook,
                grade='-'
            )

        gradebook.status = 'Не заполнена'
        gradebook.save()
        return True
    except Exception as e:
        print(f"Ошибка обновления: {e}")
        return False


def get_gradebook_name(clock_cell):
    if clock_cell.code_of_type_work == "Экзамен":
        return "Экзаменационная ведомость"
    elif clock_cell.code_of_type_work == "Зачет с оценкой":
        return "Ведомость дифференцированного зачета"
    elif clock_cell.code_of_type_work == "Другие формы контроля":
        return "Ведомость успеваемости"
    elif clock_cell.code_of_type_work == "Курсовая работа":
        return "Ведомость защиты курсового проекта"


def create_gradebook_with_fields(discipline, group, semester, grade_type, clock_cell, resist_students=None):
    try:
        gradebook = Gradebook.objects.create(
            discipline=discipline,
            group=group,
            semester_number=semester,
            type_of_grade_book=grade_type,
            name=get_gradebook_name(clock_cell),
            status='Не заполнена'
        )
        if not resist_students:
            students = Student.objects.filter(group=group)

            if is_pm_discipline(discipline):
                allowed_students = [
                    s for s in students
                    if has_required_grades(s, discipline)
                ]
            else:
                allowed_students = students

            for student in allowed_students:
                GradebookStudents.objects.create(
                    student=student,
                    gradebook=gradebook,
                    grade='-'
                )
        else:
            for student in resist_students:
                GradebookStudents.objects.create(
                    student=student,
                    gradebook=gradebook,
                    grade='-'
                )

        return True
    except Exception as e:
        print(f"Ошибка создания: {e}")
        return False


def perform_generation(semester_number, grade_book_type):
    """
    Генерирует ведомости для групп по семестру и типу.
    Учитывает все дисциплины из учебного плана и студентов группы.
    """
    generated = 0
    errors = 0

    # Оптимизированный запрос для групп
    current_course = (int(semester_number) + 1) // 2
    groups = GroupStudents.objects.filter(
        is_active=True,
        current_course=current_course
    ).select_related('qualification')

    for group in groups:
        logger.debug(f"Processing group: {group.full_name}")

        # Получаем учебный план группы
        curriculum = Curriculum.objects.filter(
            qualification=group.qualification,
            admission_year=group.year_create
        ).first()

        if not curriculum:
            logger.warning(f"No curriculum found for group {group.full_name}, qualification {group.qualification}, year {group.year_create}")
            continue

        logger.debug(f"Found curriculum: {curriculum}")

        # Выбираем необходимые ячейки часов
        clock_cells = ClockCell.objects.filter(
            curriculum=curriculum,
            term=semester_number,
            module__isnull=True,  # Заменяем module=None на isnull для надёжности
            code_of_type_work__in=[
                'Экзамен',
                'Другие формы контроля',
                'Зачет с оценкой',
                'Курсовая работа'
            ]
        ).select_related('discipline')

        if not clock_cells.exists():
            logger.warning(f"No clock cells found for curriculum {curriculum.id}, semester {semester_number}. Found {clock_cells.count()} records.")
            # Отладка: выведем все значения code_of_type_work и term
            all_cells = ClockCell.objects.filter(curriculum=curriculum).values('term', 'code_of_type_work', 'module')
            logger.debug(f"All clock cells for curriculum: {list(all_cells)}")
            continue

        logger.debug(f"Found {clock_cells.count()} clock cells for semester {semester_number}")

        for clock_cell in clock_cells:
            if not clock_cell.discipline:
                logger.warning(f"Clock cell {clock_cell.id} has no discipline")
                continue

            logger.debug(f"Processing discipline: {clock_cell.discipline.name}, type: {grade_book_type}")

            # Основная логика обработки
            if grade_book_type == "Первичная сдача":
                gradebook = Gradebook.objects.filter(
                    discipline=clock_cell.discipline,
                    group=group,
                    semester_number=semester_number,
                    type_of_grade_book=grade_book_type
                ).first()

                if gradebook and gradebook.status == "Не заполнена":
                    success = update_grade_book_contingent(
                        gradebook,
                        Student.objects.filter(group=group)
                    )
                elif not gradebook:
                    success = create_gradebook_with_fields(
                        clock_cell.discipline,
                        group,
                        semester_number,
                        grade_book_type,
                        clock_cell
                    )
                else:
                    logger.debug(f"Gradebook already exists and not 'Не заполнена' for {clock_cell.discipline.name}")
                    continue

                if success:
                    generated += 1
                    logger.info(f"Generated gradebook for {clock_cell.discipline.name}, group {group.full_name}")
                else:
                    errors += 1
                    logger.error(f"Failed to generate gradebook for {clock_cell.discipline.name}, group {group.full_name}")

            elif grade_book_type in ["Пересдача", "Комиссия"]:
                # Ищем предыдущую ведомость
                previous_type = "Первичная сдача" if grade_book_type == "Пересдача" else "Пересдача"
                primary_gradebook = Gradebook.objects.filter(
                    discipline=clock_cell.discipline,
                    group=group,
                    semester_number=semester_number,
                    type_of_grade_book=previous_type,
                    status="Закрыта"
                ).first()

                if not primary_gradebook:
                    logger.debug(f"No {previous_type} gradebook found for {clock_cell.discipline.name}")
                    continue

                # Получаем студентов с неудовлетворительными оценками
                students_for_resit = Student.objects.filter(
                    gradebookstudents__gradebook=primary_gradebook,
                    gradebookstudents__grade__in=['2', 'Неявка']
                ).distinct()

                if not students_for_resit.exists():
                    logger.debug(f"No students for {grade_book_type} in {clock_cell.discipline.name}")
                    continue

                # Проверяем существование ведомости пересдачи/комиссии
                resit_gradebook = Gradebook.objects.filter(
                    discipline=clock_cell.discipline,
                    group=group,
                    semester_number=semester_number,
                    type_of_grade_book=grade_book_type
                ).first()

                if resit_gradebook and resit_gradebook.status == 'Не заполнена':
                    success = update_grade_book_contingent(
                        resit_gradebook,
                        students_for_resit
                    )
                elif not resit_gradebook:
                    success = create_gradebook_with_fields(
                        discipline=clock_cell.discipline,
                        group=group,
                        semester=semester_number,
                        grade_type=grade_book_type,
                        clock_cell=clock_cell,
                        resist_students=students_for_resit
                    )
                else:
                    logger.debug(f"Gradebook {grade_book_type} already exists for {clock_cell.discipline.name}")
                    continue

                if success:
                    generated += 1
                    logger.info(f"Generated {grade_book_type} gradebook for {clock_cell.discipline.name}, group {group.full_name}")
                else:
                    errors += 1
                    logger.error(f"Failed to generate {grade_book_type} gradebook for {clock_cell.discipline.name}, group {group.full_name}")

    return {
        'generated': generated,
        'errors': errors,
        'grade_book_type': grade_book_type
    }


def fetch_group_semester_attestation_table(semester, group):
    """
    Функция для передачи данных на страницу статистики.
    Учитывает оценки всех студентов группы, включая восстановленных/переведённых,
    и записывает самую последнюю оценку по дисциплине на основе date_of_closing (DateTimeField).
    """
    # 1. Получаем всех студентов группы
    students = Student.objects.filter(
        group=group,
        is_expelled=False,
        is_in_academ=False
    ).order_by('full_name')

    # 2. Получаем дисциплины из учебного плана
    curriculum = Curriculum.objects.filter(
        qualification_name=group.qualification.name,
        admission_year=group.year_create
    )

    curriculum_items = ClockCell.objects.filter(
        curriculum=curriculum.first(),
        module=None,
        term=int(semester),
    ).filter(
        Q(
            code_of_type_work__in=[
                'Экзамен',
                'Другие формы контроля',
                'Зачет с оценкой',
                'Курсовая работа'
            ]
        ) |
        Q(
            discipline__code__contains='ГИА',
            discipline__name='Проведение государственных экзаменов'
        ) |
        Q(discipline__code__contains='ПДП')
    )

    disciplines = []
    for item in curriculum_items:
        if int(item.term) == int(semester) and item.discipline not in disciplines:
            discipline = Discipline.objects.get(pk=item.discipline_id)
            disciplines.append(discipline)
            print(discipline)

    # 3. Создаём матрицу студентов
    grade_matrix = {}
    for student in students:
        grade_matrix[student.id] = {
            discipline.id: "-" for discipline in disciplines
        }

    # 4. Получаем все ведомости для семестра, сортируя по дате/времени закрытия
    gradebooks = Gradebook.objects.filter(
        semester_number=semester,
        discipline__in=disciplines,
        status="Закрыта"
    ).order_by(
        F('date_of_closing').desc(nulls_last=True)
    ).prefetch_related(
        Prefetch(
            'gradebookstudents_set',
            queryset=GradebookStudents.objects.select_related('student'),
            to_attr='grades_list'
        ),
        'discipline'
    )

    # 5. Заполняем оценки, выбирая самую последнюю по date_of_closing
    for gb in gradebooks:
        discipline_id = gb.discipline.id

        for grade_entry in gb.grades_list:
            student = grade_entry.student
            student_id = student.id

            if student in students:
                # Записываем оценку только если её ещё нет
                if grade_matrix[student_id][discipline_id] == "-":
                    grade_matrix[student_id][discipline_id] = grade_entry

    return {
        'students': students,
        'disciplines': disciplines,
        'grades': grade_matrix,
        'semestr': semester,
        'group': group,
        'gradebooks': gradebooks,
        'curriculum_items': curriculum_items,
    }


class ViewStudentsGradesForSemester(ObjectTemplateView):
    """Отдельный класс для обработки статистической таблицы студентов"""
    template_name = 'Gradebook/inc/statisticks_form.html'

    def get(self, request):
        form = GetStatisticksGradebookForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GetStatisticksGradebookForm(request.POST)  # Создаем экземпляр формы

        if form.is_valid():  # Проверяем валидность ФОРМЫ
            try:
                semester = form.cleaned_data['semester']  # Данные берем из формы
                group = form.cleaned_data['group']

                data = fetch_group_semester_attestation_table(semester, group)

                return render(request, 'Gradebook/list/group_semester_grades.html', {
                    'students': data['students'],
                    'disciplines': data['disciplines'],
                    'grades': data['grades'],
                    'semestr': data['semestr'],
                    'group': data['group'],
                    'curriculum_items': data['curriculum_items'],
                })

            except Exception as e:
                print(e)
                messages.error(request,
                               "Не удалось сгенерировать статистику!")

        # Если форма невалидна, показываем ее с ошибками
        return render(request, self.template_name, {'form': form})


def export_grades(request):
    try:
        # Получение и валидация параметров
        semester = request.GET.get('semester')
        group_id = request.GET.get('group')

        if not semester or not group_id:
            raise ValueError("Не указаны обязательные параметры")

        group = get_object_or_404(GroupStudents, id=int(group_id))
        semester_number = int(semester)

    except (ValueError, TypeError) as e:
        return HttpResponse(f"Ошибка параметров: {str(e)}", status=400)
    except Exception as e:
        return HttpResponse(f"Ошибка сервера: {str(e)}", status=500)

    # Получение данных
    data = fetch_group_semester_attestation_table(semester_number, group)

    # Создание Excel-документа
    wb = Workbook()
    ws = wb.active
    ws.title = "Сводная ведомость"

    # Стили оформления
    thin_side = Side(style='thin')
    thin_border = Border(
        left=thin_side,
        right=thin_side,
        top=thin_side,
        bottom=thin_side
    )
    center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    header_fill = PatternFill(start_color='D9E1F2', fill_type='solid')
    header_font = Font(bold=True)

    # Цвета заливки
    FILLS = {
        'Первичная сдача': PatternFill(start_color='D4EDDA', fill_type='solid'),
        'Пересдача': PatternFill(start_color='CCE5FF', fill_type='solid'),
        'Комиссия': PatternFill(start_color='E2D9F3', fill_type='solid'),
        'неуд': PatternFill(start_color='FFC7CE', fill_type='solid')
    }

    # Заголовок документа
    ws.merge_cells('A1:M1')
    title_cell = ws['A1']
    title_cell.value = f"Сводная ведомость успеваемости студентов\nГруппа {group.full_name}\nСеместр {semester}"
    title_cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    title_cell.font = Font(bold=True, size=14)
    ws.row_dimensions[1].height = 60


    ws.cell(row=5, column=1, value="№ п/п").font = header_font
    ws.cell(row=5, column=2, value="Ф.И.О. студента").font = header_font
    ws.cell(row=5, column=3, value="Основа обучения").font = header_font

    # Группировка дисциплин по типам аттестации из Curriculum
    TYPE_MAPPING = {
        'Экзамен': 'Экзамены',
        'Зачет с оценкой': 'Диф. зачёты',
        'Курсовая работа': 'Курсовые работы',
        'Другие формы контроля': 'Другие формы'
    }

    # course = (semester_number + 1) // 2
    # current_term = 1 if semester_number % 2 == 1 else 2

    discipline_groups = defaultdict(list)
    for curriculum_item in data['curriculum_items']:

        if curriculum_item.term != semester_number:
            continue

        discipline = curriculum_item.discipline
        category = TYPE_MAPPING.get(
            curriculum_item.code_of_type_work,
            'Другие формы'
        )

        if discipline.id not in {d.id for d in discipline_groups[category]}:
            discipline_groups[category].append(discipline)

    # Формирование структуры таблицы
    headers = ['№ п/п', 'Ф.И.О. студента', 'Основа обучения']
    column_map = {}
    current_col = 4

    # Порядок отображения категорий
    categories_order = [
        'Экзамены',
        'Диф. зачёты',
        'Курсовые работы',
        'Другие формы'
    ]

    for category in categories_order:
        disciplines = sorted(
            discipline_groups.get(category, []),
            key=lambda x: x.name
        )

        if not disciplines:
            continue

        # Объединение ячеек для категории
        end_col = current_col + len(disciplines) - 1
        ws.merge_cells(
            start_row=4,
            start_column=current_col,
            end_row=4,
            end_column=end_col
        )
        cell = ws.cell(row=4, column=current_col, value=category)
        cell.alignment = center_alignment
        cell.fill = header_fill
        cell.font = header_font
        cell.border = thin_border

        # Добавление дисциплин
        for idx, disc in enumerate(disciplines, start=current_col):
            cell = ws.cell(row=5, column=idx, value=disc.name)
            cell.alignment = center_alignment
            cell.fill = header_fill
            cell.font = header_font
            cell.border = thin_border
            column_map[disc.id] = idx

        current_col += len(disciplines)

    # Заполнение данных студентов
    for row_idx, student in enumerate(data['students'], start=6):
        # Базовые данные
        ws.cell(row=row_idx, column=1, value=row_idx - 5).alignment = center_alignment
        ws.cell(row=row_idx, column=2, value=student.full_name)
        ws.cell(row=row_idx, column=3, value=student.education_basis).alignment = center_alignment

        # Оценки
        for category in categories_order:
            for disc in discipline_groups.get(category, []):
                col = column_map.get(disc.id)
                if not col:
                    continue

                grade_entry = data['grades'].get(student.id, {}).get(disc.id)

                cell = ws.cell(row=row_idx, column=col)
                cell.alignment = center_alignment
                cell.border = thin_border

                if grade_entry:
                    if grade_entry == "-":
                        cell.value = grade_entry
                    else:
                        cell.value = grade_entry.grade

                        if str(grade_entry.grade).lower() in ['неудовлетворительно', 'неявка', 'н/я', '2']:
                            cell.fill = FILLS['неуд']
                        elif grade_entry.gradebook.type_of_grade_book in FILLS:
                            cell.fill = FILLS[grade_entry.gradebook.type_of_grade_book]

    # Настройка ширины столбцов
    for col_idx in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = 20 if col_idx > 3 else 15

    # Применение стилей ко всем ячейкам
    for row in ws.iter_rows():
        for cell in row:
            cell.border = thin_border
            if cell.row > 5 and cell.column in [1, 3]:
                cell.alignment = center_alignment

    # Формирование имени файла
    group_name_clean = unidecode(group.full_name)
    group_name_clean = re.sub(r'\W+', '_', group_name_clean)[:50]
    filename = f"Vedomost_{group_name_clean}_sem{semester}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


def get_disciplines_with_last_semester(group):
    """Возвращает список дисциплин с последним семестром, часами и общей суммой часов."""
    logger.info(f"Fetching disciplines for group {group.full_name}")
    clock_cells = ClockCell.objects.filter(
        curriculum__qualification=group.qualification,
        curriculum__admission_year=group.year_create
    ).select_related('discipline', 'module').order_by('discipline__id', '-term')

    # Словарь для хранения последнего семестра, часов и имени по каждой дисциплине
    last_semesters = defaultdict(int)
    total_hours = defaultdict(int)
    display_names = {}  # Для хранения имени (дисциплина или модуль)

    for cell in clock_cells:
        discipline = cell.discipline
        module = cell.module
        discipline_id = None

        if discipline:
            discipline_id = discipline.id
            # Обновляем последний семестр
            if cell.term > last_semesters[discipline_id]:
                last_semesters[discipline_id] = cell.term
            # Проверяем, содержит ли код дисциплины "ПМ"
            if discipline and 'ПM' in discipline.code.upper().strip():
                # Ищем модуль с discipline=None и совпадающим кодом
                module_cells = ClockCell.objects.filter(
                    curriculum__qualification=group.qualification,
                    curriculum__admission_year=group.year_create,
                    discipline__isnull=True,
                    module__isnull=False,
                    code_of_type_work='Итого часов'
                ).select_related('module')
                for mc in module_cells:
                    if mc.module and mc.module.code_of_discipline.strip() in discipline.code.replace('M', 'М').strip():
                        total_hours[discipline_id] = mc.count_of_clocks
                        display_names[discipline_id] = mc.module.name.strip()
                        logger.debug(f"Using module {mc.module.name} for discipline {discipline.name}: {mc.count_of_clocks} hours")
                        break
                else:
                    # Если модуль не найден, используем часы дисциплины
                    if cell.code_of_type_work == 'Итого часов':
                        total_hours[discipline_id] += cell.count_of_clocks
                        display_names[discipline_id] = discipline.name
                        logger.debug(f"Using discipline {discipline.name}: {cell.count_of_clocks} hours")
            else:
                # Для обычных дисциплин
                if cell.code_of_type_work == 'Итого часов':
                    total_hours[discipline_id] += cell.count_of_clocks
                    display_names[discipline_id] = discipline.name
                    logger.debug(f"Adding {cell.count_of_clocks} hours for {discipline.name}")

    # Получаем объекты дисциплин с последними семестрами, часами и именами
    disciplines_with_semesters = []
    for discipline_id, last_term in last_semesters.items():
        discipline = Discipline.objects.get(id=discipline_id)
        hours = total_hours.get(discipline_id, 0)
        name = display_names.get(discipline_id, discipline.name)
        disciplines_with_semesters.append((discipline, last_term, hours, name))
        logger.debug(f"Discipline: {discipline.name}, display name: {name}, semester: {last_term}, hours: {hours}")

    # Сортируем по коду дисциплины
    disciplines_with_semesters.sort(key=lambda x: x[0].code)

    # Подсчитываем общую сумму часов
    total_all_hours = sum(hours for _, _, hours, _ in disciplines_with_semesters)
    logger.info(f"Total hours: {total_all_hours}")

    logger.info(f"Returning {len(disciplines_with_semesters)} disciplines")
    return disciplines_with_semesters, total_all_hours


class DiplomTypeIdentifier(ObjectTemplateView):
    template_name = "Gradebook/inc/diplom_type_form.html"

    def get(self, request):
        form = GetDiplomTypeGradebookForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GetDiplomTypeGradebookForm(request.POST)

        if form.is_valid():
            try:
                form_group = form.cleaned_data['group']
                group = GroupStudents.objects.get(id=form_group.id)
                logger.info(f"Processing group: {group.full_name}")

                # Получаем дисциплины и общую сумму часов
                disciplines_with_semesters, total_all_hours = get_disciplines_with_last_semester(group)
                if not disciplines_with_semesters:
                    logger.warning(f"No disciplines found for group {group.full_name}")
                    messages.error(request, "Для выбранной группы нет дисциплин")
                    return render(request, self.template_name, {'form': form})

                logger.info(f"Disciplines: {[(d[0].name, d[1], d[2], d[3]) for d in disciplines_with_semesters]}")
                semesters_order = sorted({d[1] for d in disciplines_with_semesters})

                context = {
                    'group': group,
                    'students': Student.objects.filter(group=group, is_expelled=False, is_in_academ=False),
                    'disciplines_with_semesters': disciplines_with_semesters,
                    'semesters_order': semesters_order,
                    'total_all_hours': total_all_hours,
                    'current_year': timezone.now().year,
                    'education_basis': 'После 11 класса' if group.education_base == 'Среднее общее' else 'После 9 класса'
                }

                return render(request, 'Gradebook/list/diplom_type_identifier.html', context)
            except Exception as e:
                logger.error(f"Error calculating diploma types: {str(e)}", exc_info=True)
                messages.error(request, f"Не удалось рассчитать тип дипломов: {str(e)}")
        else:
            logger.warning(f"Invalid form data: {form.errors}")
            messages.error(request, "Некорректные данные формы")

        return render(request, self.template_name, {'form': form})


class GradebookTableView(ObjectTableView):
    """
    Класс для отображения таблицы ведомостей.
    """
    table_class = GradebookTable
    filterset_class = GradebookFilter
    queryset = Gradebook.objects.all()

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(Gradebook, 'add'),
            permission = getpermission(Gradebook, 'add'),
        ),
        Button(
            id = 'generate',
            name = 'Сгенерировать ведомости',
            link_name = 'gradebook_generate',
            permission = getpermission(Gradebook, 'add'),
        )
    ]
    queryset = Gradebook.objects.exclude(status=Gradebook.STATUS_CHOICE[3][1])

    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return GradebookTable

    def get(self, request, *args, **kwargs):

        is_closed = request.GET.get('is_closed', None)
        is_filled = request.GET.get('is_filled', None)

        if is_closed:
            messages.success(request, "Ведомость успешно закрыта!")
        if is_filled:
            messages.success(request, "Ведомость успешно заполнена!")

        base_url = reverse('gradebook_list')
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        if query_params:
            request.session['gradebook_return_to'] = f"{base_url}?{query_params.urlencode()}"
        else:
            request.session['gradebook_return_to'] = base_url


        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GenerateGradebookForm()  # Доп. форма
        return context


class GradebookClosedList(ObjectTableView):
    table_class = GradebookTable
    filterset_class = ClosedGradebookFilter
    queryset = Gradebook.objects.filter(status=Gradebook.STATUS_CHOICE[3][1])
    properties = {}

    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return GradebookTable

    def get(self, request, *args, **kwargs):
        base_url = reverse('gradebookclosed_list')
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        if query_params:
            request.session['gradebook_return_to'] = f"{base_url}?{query_params.urlencode()}"
        else:
            request.session['gradebook_return_to'] = base_url
        return super().get(request, *args, **kwargs)

class TeachersGradeBookTableView(ObjectTableView):
    permission_required = None
    table_class = TeacherGradeBookTable
    filterset_class = GradeBookTeachersFilter
    queryset = Gradebook.objects.all() 

    def get_queryset(self):
        # Получаем залогиненного пользователя
        user = get_object_or_404(CustomUser, pk=self.request.user.pk)

        # Проверка аутентификации и прав преподавателя
        if not user.is_authenticated or not hasattr(user, 'is_teacher') or not user.is_teacher:
            return Gradebook.objects.none()

        # Фильтрация ведомостей
        queryset = Gradebook.objects.filter(
            status='Открыта',  # Статус "Открыта"
            teachers__id=user.id  # Текущий пользователь в списке преподавателей
        ).select_related(  # Оптимизация запросов
            'group',
            'discipline'
        ).prefetch_related(
            'teachers',
            'students'
        ).distinct()  # Убираем дубликаты

        return queryset
 
    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return TeacherGradeBookTable

    def get(self, request, *args, **kwargs):

        is_filled = request.GET.get('is_filled', None)

        if is_filled:
            messages.success(request, "Ведомость успешно заполнена!")

        base_url = reverse('gradebookteacher_list')
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        if query_params:
            request.session['gradebook_return_to'] = f"{base_url}?{query_params.urlencode()}"
        else:
            request.session['gradebook_return_to'] = base_url

        return super().get(request, *args, **kwargs)


class GradebookRedirectView(View):
    def get(self, request, *args, **kwargs):
        # Получаем URL из сессии, по умолчанию редиректим на 'gradebook:list'
        return_to = request.session.get('gradebook_return_to', reverse('gradebook_list'))
        return redirect(return_to)

class GradebookDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации об учебном журнале.
    """
    model= Gradebook
    paginate_by   = 30
    template_name = 'Gradebook/detail/gradebook_student.html'

    fieldset = {
        'Основная информация': [
            'name', 'discipline','status', 'number', 'type_of_grade_book', 'group', 'semester_number'
        ],
        'Дополнительная информация': [
            'date_of_opening', 'date_of_filling', 'date_of_closing',
            'amount_of_days_for_closing'
        ]
    }


    def check_status(obj, user):
        return obj.status == "Не заполнена"

    # Формируем список кнопок динамически
    buttons = [
        Button(
            id='change',
            name='Изменить',
            link_params=['pk'],
            link_name=getpattern(Gradebook, 'change'),
            permission=getpermission(Gradebook, 'change'),
        ),
        Button(
            id='to_list',
            name='К таблице',
            link_name='redirect_to_list',
            permission=getpermission(Gradebook, 'view')
        ),
        Button(
            link_params=['pk'],
            name='Открыть ведомость',
            link_name='check_open_gradebook',
            condition=lambda obj, user: obj.status == "Не заполнена"
        ),
        Button(
            link_params=['pk'],
            name='Закрыть ведомость',
            link_name='download_report',
            condition=lambda obj, user: obj.status == "Заполнена"
        ),
        Button(
            link_params=['pk'],
            name='Скачать документ',
            link_name='download_report',
            condition=lambda obj, user: obj.status == "Закрыта"
        )
    ]

    def grade_book_student_filter(self, queryset):
        if queryset.filter(gradebook_id=self.pk).count() == 0:
            return GradebookStudents.objects.filter(gradebook=self.pk)
        return queryset.filter(gradebook__id=self.pk)

    def grade_book_teacher_filter(self, queryset):
        return self.teachers.all()

    tables = [
        SubTable (
            name='Студенты',
            table=GradebookStudentsTable,
            queryset=GradebookStudents.objects.all(),
            filter_func=grade_book_student_filter,
            buttons=[
                Button (
                    name = 'Заполнить ведомость',
                    link_name = 'gradebookstudents_bulk_create',
                    link_params = ['pk'],
                    condition= lambda obj, user: obj.status == "Открыта"
                )
            ]
        ),
        SubTable(
            name='Учителя',
            queryset=CustomUser.objects.all(),
            table=GradebookTeachersTable,
            filter_func=grade_book_teacher_filter
        )
    ]

    def get(self, request, *args, **kwargs):
        gradebook = self.get_object()

        is_active = request.GET.get('is_active',None)

        # Проверка основных полей
        required_fields = [
            gradebook.group_id,  # Проверка ForeignKey через id
            gradebook.discipline_id,  # Проверка ForeignKey дисциплины
            gradebook.semester_number,  # Проверка IntegerField
            gradebook.status,  # Проверка CharField статуса
        ]

        # Проверка текстовых полей на непустые значения
        text_fields_valid = all([
            gradebook.status and gradebook.status.strip(),
        ])

        relations_valid = all([
            gradebook.teachers.exists(),  # Проверка наличия преподавателей
            gradebook.students.exists(),  # Проверка наличия студентов
        ])

        # Комплексная проверка всех условий
        if not all(required_fields) or not text_fields_valid or not relations_valid:
            messages.error(
                request,
                "Невозможно открыть ведомость! Заполните все обязательные поля: "
                "группа, дисциплина, название, статус, семестр, преподаватели и студенты."
            )
        else:
            if is_active:
                messages.success(request, "Ведомость успешно открыта!")

        return super().get(request, *args, **kwargs)

class GradebookUpdateView(GradeBookMixin, ObjectUpdateView):
    """
    Класс для обновления информации об учебном журнале.
    """
    form_class = GradebookForm
    queryset = Gradebook.objects.all()
    properties = {}

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(Gradebook, 'detail'),
            permission = getpermission(Gradebook, 'view')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Gradebook, 'list'),
            permission = getpermission(Gradebook, 'view')
        )
    ]



class GradebookCreateView(GradeBookMixin, ObjectCreateView):
    """
    Класс для создания нового учебного журнала.
    """
    model = Gradebook
    form_class = GradebookForm
    template_name = 'Gradebook/create/grade_book.html'
    properties = ['group_id']

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Gradebook, 'list'),
            permission = getpermission(Gradebook, 'view')
        )
    ]


def get_download_path() -> Path:
    """
    Возвращает путь к папке загрузок в зависимости от ОС.
    Поддерживает: Windows, macOS, Linux, Android (Termux), iOS (Pythonista).
    Для других случаев возвращает текущую директорию.
    """
    # Для Android (Termux)
    if "ANDROID_ROOT" in os.environ:
        return Path("/storage/emulated/0/Download")

    # Для iOS (Pythonista)
    if sys.platform == "ios":
        return Path(os.path.expanduser("~/Documents"))

    # Для Windows
    if sys.platform == "win32":
        return Path(os.path.join(os.environ["USERPROFILE"], "Downloads"))

    # Для macOS и Linux
    download_dir = ""

    # Проверка XDG для Linux
    if sys.platform == "linux":
        download_dir = os.environ.get("XDG_DOWNLOAD_DIR", "")
        if download_dir:
            return Path(download_dir)

    # Стандартные пути для macOS/Linux/других Unix
    home = Path.home()
    possible_paths = [
        home / "Downloads",
        home / "Download",
        home / "downloads",
        home / "Загрузки"  # Для русскоязычных систем
    ]

    # Поиск существующей папки
    for path in possible_paths:
        if path.exists():
            return path

    # Fallback: текущая директория
    return Path.cwd()


logger = logging.getLogger(__name__)

# @permission_required(getpermission(Gradebook, 'view'))
# def download_report(request, pk):
#     try:
#         # Получение объекта Gradebook
#         logger.info(f"Fetching Gradebook with pk={pk}")
#         gradebook = get_object_or_404(
#             Gradebook.objects.select_related('discipline', 'group__qualification__specialty').prefetch_related('teachers', 'students'),
#             pk=pk
#         )
#
#         # Логика изменения статуса
#         logger.info(f"Current status: {gradebook.status}")
#         if gradebook.status == Gradebook.STATUS_CHOICE[2][1]:
#             logger.info("Updating gradebook status and closing date")
#             gradebook.status = Gradebook.STATUS_CHOICE[3][1]
#             gradebook.date_of_closing = timezone.now()
#             gradebook.save()
#
#         # Генерация документа
#         file_name = f"{gradebook.name.replace(' ', '_')}_{gradebook.discipline.name}_{gradebook.semester_number}_{gradebook.group.full_name}.docx"
#         logger.info(f"Generating document: {file_name}")
#
#         generator = GradebookDocumentGenerator(gradebook)
#         buffer = generator.generate_document()
#
#         # Отправка файла
#         logger.info(f"Sending file: {file_name}")
#         response = FileResponse(
#             buffer,
#             content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
#         )
#         response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(file_name)}'
#         return response
#
#     except Exception as e:
#         logger.error(f"Error in download_report: {str(e)}", exc_info=True)
#         return HttpResponse(f"Произошла ошибка: {str(e)}", status=500)


@permission_required(getpermission(Gradebook, 'view'))
def download_report(request, pk):
    try:
        gradebook = get_object_or_404(
            Gradebook.objects.select_related('discipline', 'group__qualification__specialty').prefetch_related('teachers', 'students'),
            pk=pk
        )

        if gradebook.status == Gradebook.STATUS_CHOICE[2][1]:
            gradebook.status = Gradebook.STATUS_CHOICE[3][1]
            gradebook.date_of_closing = timezone.now()
            gradebook.save()

        file_name = f"{gradebook.name.replace(' ', '_')}_{gradebook.discipline.name}_{gradebook.semester_number}_{gradebook.group.full_name}.docx"
        generator = GradebookDocumentGenerator(gradebook)
        buffer = generator.generate_document()

        response = FileResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(file_name)}'
        response['X-Refresh-After'] = reverse('gradebook_detail', kwargs={'pk': pk})
        return response

    except Exception as e:
        logger.error(f"Error in download_report: {str(e)}", exc_info=True)
        return HttpResponse(f"Произошла ошибка: {str(e)}", status=500)

@permission_required(getpermission(Gradebook, 'view'))
def check_and_open_gradebook(request, pk):
    """
    Проверяет заполненность всех обязательных полей ведомости,
    включая наличие связанных преподавателей и студентов.
    """
    gradebook = get_object_or_404(Gradebook, id=pk)

    # Проверка основных полей
    required_fields = [
        gradebook.group_id,  # Проверка ForeignKey через id
        gradebook.name,  # Проверка CharField
        gradebook.discipline_id,  # Проверка ForeignKey дисциплины
        gradebook.semester_number,  # Проверка IntegerField
        gradebook.status,  # Проверка CharField статуса
    ]

    # Проверка текстовых полей на непустые значения
    text_fields_valid = all([
        gradebook.name and gradebook.name.strip(),
        gradebook.status and gradebook.status.strip(),
    ])

    # Проверка связей ManyToMany и ForeignKey
    relations_valid = all([
        gradebook.teachers.exists(),  # Проверка наличия преподавателей
        gradebook.students.exists(),  # Проверка наличия студентов
    ])

    # Комплексная проверка всех условий
    if not all(required_fields) or not text_fields_valid or not relations_valid:
        return redirect('gradebook_detail', pk=pk)

    # Обновление статуса и даты
    gradebook.status = "Открыта"
    gradebook.date_of_opening = timezone.now().date()
    gradebook.save()

    response = redirect('gradebook_detail', pk=pk)
    response['Location'] += '?is_active=true'
    return response


def export_diplom_types(request):
    """Экспортирует таблицу успеваемости и типов диплома в Excel."""
    group_id = request.GET.get('group')
    if not group_id:
        logger.error("No group ID provided for export")
        return HttpResponse("Группа не указана", status=400)

    try:
        group = get_object_or_404(GroupStudents, id=group_id)
        logger.info(f"Exporting diplom types for group {group.full_name}")

        # Получаем дисциплины и общую сумму часов
        disciplines_with_semesters, total_all_hours = get_disciplines_with_last_semester(group)
        if not disciplines_with_semesters:
            logger.warning(f"No disciplines found for group {group.full_name}")
            return HttpResponse("Для выбранной группы нет дисциплин", status=404)

        students = Student.objects.filter(group=group, is_expelled=False, is_in_academ=False)
        semesters_order = sorted({d[1] for d in disciplines_with_semesters})

        # Сортируем дисциплины по семестрам для一致ности
        sorted_disciplines = []
        for semester in semesters_order:
            semester_disciplines = [d for d in disciplines_with_semesters if d[1] == semester]
            sorted_disciplines.extend(sorted(semester_disciplines, key=lambda x: x[0].name))

        # Подготовка оценок с учетом типов ведомостей
        grades_data = {}
        for student in students:
            grades_data[student.id] = {}
            for discipline, semester, _, _ in sorted_disciplines:
                gradebooks = student.gradebookstudents_set.filter(
                    gradebook__discipline=discipline,
                    gradebook__semester_number=semester
                )

                # Логика получения оценки
                primary_grade = gradebooks.filter(gradebook__type_of_grade_book='Первичная сдача').first()

                if primary_grade and primary_grade.grade in ['2', 'неявка', 'н/я']:
                    retake_grade = gradebooks.filter(gradebook__type_of_grade_book='Пересдача').first()

                    if retake_grade and retake_grade.grade in ['2', 'неявка', 'н/я']:
                        commission_grade = gradebooks.filter(gradebook__type_of_grade_book='Комиссия').first()
                        if commission_grade:
                            grades_data[student.id][(discipline.id, semester)] = commission_grade
                        else:
                            grades_data[student.id][(discipline.id, semester)] = retake_grade
                    elif retake_grade:
                        grades_data[student.id][(discipline.id, semester)] = retake_grade
                    else:
                        grades_data[student.id][(discipline.id, semester)] = primary_grade
                elif primary_grade:
                    grades_data[student.id][(discipline.id, semester)] = primary_grade
                else:
                    retake_grade = gradebooks.filter(gradebook__type_of_grade_book='Пересдача').first()
                    if retake_grade and retake_grade.grade in ['2', 'неявка', 'н/я']:
                        commission_grade = gradebooks.filter(gradebook__type_of_grade_book='Комиссия').first()
                        if commission_grade:
                            grades_data[student.id][(discipline.id, semester)] = commission_grade
                        else:
                            grades_data[student.id][(discipline.id, semester)] = retake_grade
                    elif retake_grade:
                        grades_data[student.id][(discipline.id, semester)] = retake_grade
                    else:
                        commission_grade = gradebooks.filter(gradebook__type_of_grade_book='Комиссия').first()
                        grades_data[student.id][(discipline.id, semester)] = commission_grade

                grade_obj = grades_data[student.id].get((discipline.id, semester))
                logger.debug(
                    f"Pre-fetched grade for {student.full_name}, {discipline.name}, semester {semester}: {grade_obj.grade if grade_obj else None}, type={grade_obj.gradebook.type_of_grade_book if grade_obj else None}")

        # Создаём Excel-файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Сводная ведомость"

        # Стили
        bold_font = Font(bold=True)
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # Цвета
        FILLS = {
            'Первичная сдача': PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid"),
            'Пересдача': PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid"),
            'Комиссия': PatternFill(start_color="9370DB", end_color="9370DB", fill_type="solid"),
            'неуд': PatternFill(start_color="F5C6CB", end_color="F5C6CB", fill_type="solid")
        }
        red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
        blue_fill = PatternFill(start_color="2196F3", end_color="2196F3", fill_type="solid")

        # Заголовок
        education_basis = 'После 11 класcа' if group.education_base == 'Среднее общее' else 'После 9 класса'
        ws.append([f"СПЕЦИАЛЬНОСТЬ {group.qualification.name} ({education_basis})"])
        ws.append([f"СВОДНАЯ ВЕДОМОСТЬ УСПЕВАЕМОСТИ СТУДЕНТОВ ГРУППЫ {group.full_name}"])
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=2 + len(sorted_disciplines) + 1)
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=2 + len(sorted_disciplines) + 1)
        for row in ws[1:2]:
            for cell in row:
                cell.font = bold_font
                cell.alignment = center_align

        # Легенда с цветами
        ws.append([])
        ws.append(["Легенда:"])
        ws.append(["Первичная сдача", "Оценка при первой попытке"])
        ws.append(["Пересдача", "Оценка при пересдаче"])
        ws.append(["Комиссия", "Оценка через комиссию"])
        ws.append(["2 или н/я", "Неудовлетворительная оценка или неявка"])
        ws['A5'].fill = FILLS['Первичная сдача']
        ws['A6'].fill = FILLS['Пересдача']
        ws['A7'].fill = FILLS['Комиссия']
        ws['A8'].fill = FILLS['неуд']
        for row in ws[4:8]:
            for cell in row[:2]:
                cell.border = thin_border
                cell.alignment = center_align
            if row[0].row in [4, 5]:
                row[0].font = bold_font

        # Заголовок таблицы
        header_row = ["№", "ФИО студента"]
        for discipline, disp_semester, hours, display_name in sorted_disciplines:
            header_row.append(f"{discipline.code} {display_name} (Семестр {disp_semester})")
        header_row.append("Тип диплома")
        ws.append([])
        ws.append(header_row)
        header_row_num = ws.max_row

        # Строка с часами
        hours_row = ["", "Часы"]
        for discipline, disp_semester, hours, display_name in sorted_disciplines:
            hours_row.append(hours or 0)
        hours_row.append(total_all_hours or 0)
        ws.append(hours_row)

        # Данные студентов
        for idx, student in enumerate(students, 1):
            row = [idx, student.full_name]
            for discipline, disp_semester, hours, display_name in sorted_disciplines:
                grade_obj = grades_data[student.id].get((discipline.id, disp_semester))
                row.append(grade_obj.grade if grade_obj else "-")
            # Тип диплома
            grades = []
            for discipline, semester, hours, display_name in sorted_disciplines:
                grade = grades_data[student.id].get((discipline.id, semester))
                grades.append(grade)
            bad_grades = [g for g in grades if
                          g and str(g.grade).lower() in ['2', 'неявка', 'н/я', 'неудовлетворительно']]
            valid_grades = [g for g in grades if
                            g and str(g.grade).lower() not in ['2', 'неявка', 'н/я', 'неудовлетворительно']]
            count_4 = len([g for g in valid_grades if g.grade == '4'])
            total_grades = len(valid_grades)
            diploma_type = "Синий" if bad_grades or (total_grades and count_4 < total_grades * 0.25) else "Красный"
            row.append(diploma_type)
            ws.append(row)

        # Форматирование таблицы
        for row in ws[header_row_num:ws.max_row]:
            for cell in row:
                cell.border = thin_border
                cell.alignment = center_align
        for cell in ws[header_row_num]:
            cell.font = bold_font
        for cell in ws[header_row_num + 1]:
            cell.font = bold_font

        # Установка ширины столбцов
        ws.column_dimensions['A'].width = 5  # №
        ws.column_dimensions['B'].width = 30  # ФИО
        for col in range(3, len(sorted_disciplines) + 3):
            ws.column_dimensions[get_column_letter(col)].width = 10  # Дисциплины
        ws.column_dimensions[get_column_letter(len(sorted_disciplines) + 3)].width = 15  # Тип диплома

        # Применение цветов для оценок и диплома
        for row_idx in range(header_row_num + 2, ws.max_row + 1):
            student = students[row_idx - (header_row_num + 2)]
            for col_idx, (discipline, semester, _, _) in enumerate(sorted_disciplines, start=3):
                cell = ws.cell(row=row_idx, column=col_idx)
                grade = cell.value
                logger.debug(f"Processing cell ({row_idx}, {col_idx}): value={grade}")
                if grade and grade != "-":
                    grade_obj = grades_data[student.id].get((discipline.id, semester))
                    if grade_obj:
                        grade_str = str(grade_obj.grade).lower()
                        type_of_grade = str(grade_obj.gradebook.type_of_grade_book).lower().strip()
                        logger.debug(
                            f"Grade for {student.full_name}, {discipline.name}: grade={grade_str}, type={type_of_grade}")
                        if grade_str in ['2', 'неявка', 'н/я', 'неудовлетворительно']:
                            cell.fill = FILLS['неуд']
                            logger.debug(f"Applied неуд fill for {grade_str}")
                        elif type_of_grade == 'первичная сдача':
                            cell.fill = FILLS['Первичная сдача']
                            logger.debug(f"Applied Первичная сдача fill")
                        elif type_of_grade == 'пересдача':
                            cell.fill = FILLS['Пересдача']
                            logger.debug(f"Applied Пересдача fill")
                        elif type_of_grade == 'комиссия':
                            cell.fill = FILLS['Комиссия']
                            logger.debug(f"Applied Комиссия fill")
                    else:
                        logger.debug(
                            f"No grade_obj found for {student.full_name}, {discipline.name}, semester {semester}")
            # Цвет для типа диплома
            diploma_cell = ws.cell(row=row_idx, column=len(sorted_disciplines) + 3)
            logger.debug(f"Diploma cell ({row_idx}, {len(sorted_disciplines) + 3}): value={diploma_cell.value}")
            if diploma_cell.value == "Красный":
                diploma_cell.fill = red_fill
                diploma_cell.font = Font(color="FFFFFF")
            elif diploma_cell.value == "Синий":
                diploma_cell.fill = blue_fill
                diploma_cell.font = Font(color="FFFFFF")

        # Сохранение файла
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Diplom_Types_{group.full_name}.xlsx"'
        wb.save(response)
        logger.info(f"Excel file generated for group {group.full_name}")
        return response

    except Exception as e:
        logger.error(f"Error exporting diplom types: {str(e)}", exc_info=True)
        return HttpResponse(f"Ошибка при экспорте: {str(e)}", status=500)