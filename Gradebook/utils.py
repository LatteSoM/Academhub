import logging
import re
from django.core.cache import cache

from django.db.models import Func, Q, F, Prefetch

from Academhub.models import Gradebook, Discipline, ClockCell, Student, GradebookStudents
from collections import defaultdict

from Academhub.models.models import TeachersForDisciplineAndCurriculum, Curriculum, GroupStudents

logger = logging.getLogger(__name__)


def update_gradebooks_after_deactivation(teachers):
    """
    Удаляет деактивированных преподавателей из ведомостей и обновляет статус.

    Args:
        teachers (QuerySet): Список деактивированных преподавателей.
    """
    try:
        # Получаем ведомости со статусом "Открыта" или "Не заполнена"
        gradebooks = Gradebook.objects.filter(status__in=['Открыта', 'Не заполнена'])

        if not gradebooks.exists():
            logger.info("Нет ведомостей со статусом 'Открыта' или 'Не заполнена' для обработки.")
            return

        # Обрабатываем каждую ведомость
        for gradebook in gradebooks:
            # Проверяем, есть ли деактивированные преподаватели в ведомости
            teachers_to_remove = gradebook.teachers.filter(id__in=teachers.values_list('id', flat=True))

            if teachers_to_remove.exists():
                # Удаляем преподавателей из ведомости
                gradebook.teachers.remove(*teachers_to_remove)

                # Устанавливаем статус "Не заполнена"
                gradebook.status = 'Не заполнена'
                gradebook.save()

                logger.info(
                    f"Ведомость {gradebook.number} ({gradebook.name}) обновлена: удалены преподаватели {list(teachers_to_remove.values_list('email', flat=True))}, статус изменен на 'Не заполнена'.")
            else:
                logger.debug(
                    f"Ведомость {gradebook.number} ({gradebook.name}) не содержит деактивированных преподавателей.")

    except Exception as e:
        logger.error(f"Ошибка при обновлении ведомостей: {str(e)}")
        raise

def transliterate(text):
    translit_dict = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
        'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
        'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
        'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu',
        'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
        'я': 'ya'
    }
    return ''.join(translit_dict.get(char, char) for char in text)


def get_disciplines_with_last_semester(group):
    """Возвращает список дисциплин с последним семестром, часами и общей суммой часов."""
    logger.info(f"Fetching disciplines for group {group.full_name}")
    group_edu_base = 9 if group.education_base == "Основное общее" else 11

    clock_cells = ClockCell.objects.filter(
        curriculum__qualification=group.qualification,
        curriculum__admission_year=group.year_create,
        curriculum__basis_of_admission=group_edu_base
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
                    curriculum__basis_of_admission=group_edu_base,
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


class Strip(Func):
    function = 'TRIM'
    template = '%(function)s(%(expressions)s)'

def is_pm_discipline(discipline):
    """Проверяет, является ли дисциплина ПМ по формату кода ПМ.XX.XXX"""
    code = str(discipline.code).strip().upper()
    return re.match(r'^П[МM]\.\d{2}\.', code, re.IGNORECASE) is not None

def extract_pm_number(pm_code):
    """Извлекает номер из кода ПМ (например, '01' из 'ПМ.01.ЭК')"""
    normalized_code = str(pm_code).upper().replace("M", "М")
    match = re.match(r"^ПМ\.(\d{2})\..*", normalized_code)
    return match.group(1) if match else None

def get_required_prefixes(pm_number):
    """Генерирует префиксы для проверяемых дисциплин"""
    return [
        f'МДК.{pm_number}.',
        f'УП.{pm_number}.',
        f'ПП.{pm_number}.'
    ]

def has_required_grades(student, pm_discipline):
    """
    Проверяет, имеет ли студент допустимую оценку (3, 4, 5) в последней ведомости
    по каждой дисциплине с соответствующими кодами.
    """
    pm_number = extract_pm_number(pm_discipline.code)
    if not pm_number:
        logger.warning(f"Invalid PM code: {pm_discipline.code}")
        return False

    prefixes = get_required_prefixes(pm_number)

    # Оптимизированный запрос для дисциплин
    disciplines = Discipline.objects.annotate(
        clean_code=Strip('code')
    ).filter(
        Q(clean_code__startswith=prefixes[0]) |
        Q(clean_code__startswith=prefixes[1]) |
        Q(clean_code__startswith=prefixes[2])
    ).prefetch_related(
        Prefetch(
            'gradebooks',
            queryset=Gradebook.objects.order_by('-date_of_closing')
        )
    )

    valid_grades = {'3', '4', '5'}
    invalid_grades = {'2', 'н/я', '-'}

    for discipline in disciplines:
        latest_gradebook = discipline.gradebooks.first()
        if not latest_gradebook:
            logger.debug(f"No gradebook for discipline: {discipline.name}")
            return False

        grade_entry = GradebookStudents.objects.filter(
            student=student,
            gradebook=latest_gradebook
        ).first()

        if not grade_entry or grade_entry.grade not in valid_grades or grade_entry.grade in invalid_grades:
            logger.debug(f"Invalid grade for {student.full_name} in {discipline.name}: {grade_entry.grade if grade_entry else 'None'}")
            return False

    return True


def update_grade_book_contingent(gradebook, students):
    try:
        # Обновляем преподавателей
        teacher_link = TeachersForDisciplineAndCurriculum.get_teachers_for_gradebook(
            discipline=gradebook.discipline,
            group=gradebook.group,
            semester=gradebook.semester_number
        )

        if teacher_link:
            gradebook.teachers.set(teacher_link.teachers.all())

        # Удаляем старые записи
        GradebookStudents.objects.filter(gradebook=gradebook).delete()

        if is_pm_discipline(gradebook.discipline):
            students = [s for s in students if has_required_grades(s, gradebook.discipline)]

        # Массовое создание новых записей
        gradebook_students = [
            GradebookStudents(student=student, gradebook=gradebook, grade='-')
            for student in students
        ]
        GradebookStudents.objects.bulk_create(gradebook_students)

        gradebook.status = 'Не заполнена'
        gradebook.save()
        return True
    except Exception as e:
        logger.error(f"Ошибка обновления ведомости: {str(e)}", exc_info=True)
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
        # Получаем привязанных преподавателей
        teacher_link = TeachersForDisciplineAndCurriculum.get_teachers_for_gradebook(
            discipline=discipline,
            group=group,
            semester=semester
        )

        gradebook = Gradebook.objects.create(
            discipline=discipline,
            group=group,
            semester_number=semester,
            type_of_grade_book=grade_type,
            name=get_gradebook_name(clock_cell),
            status='Не заполнена'
        )

        # Назначаем преподавателей
        if teacher_link:
            gradebook.teachers.set(teacher_link.teachers.all())

        # Обработка студентов
        students = resist_students if resist_students else Student.objects.filter(group=group)

        if is_pm_discipline(discipline):
            students = [s for s in students if has_required_grades(s, discipline)]

        # Массовое создание записей GradebookStudents
        gradebook_students = [
            GradebookStudents(student=student, gradebook=gradebook, grade='-')
            for student in students
        ]
        GradebookStudents.objects.bulk_create(gradebook_students)

        return True
    except Exception as e:
        logger.error(f"Ошибка создания ведомости: {str(e)}", exc_info=True)
        return False


def perform_generation(semester_number, grade_book_type):
    """
    Генерирует ведомости для групп по семестру и типу.
    Учитывает все дисциплины из учебного плана и студентов группы.
    """
    generated = 0
    updated = 0
    errors = 0

    # Оптимизированный запрос для групп
    current_course = (int(semester_number) + 1) // 2
    groups = GroupStudents.objects.filter(
        is_active=True,
        current_course=current_course
    ).select_related('qualification').prefetch_related(
        Prefetch(
            'students',
            queryset=Student.objects.filter(is_expelled=False, is_in_academ=False)
        )
    )

    for group in groups:
        logger.debug(f"Processing group: {group.full_name}")

        group_edu_base = 9 if group.education_base == "Основное общее" else 11

        # Кэшируем учебный план
        cache_key = f"curriculum_{group.id}_{semester_number}"
        curriculum = cache.get(cache_key)
        if not curriculum:
            curriculum = Curriculum.objects.filter(
                qualification=group.qualification,
                admission_year=group.year_create,
                basis_of_admission=group_edu_base
            ).first()
            cache.set(cache_key, curriculum, 3600)  # Кэш на 1 час

        if not curriculum:
            logger.warning(f"No curriculum found for group {group.full_name}")
            continue

        # Выбираем необходимые ячейки часов
        clock_cells = ClockCell.objects.filter(
            curriculum=curriculum,
            term=semester_number,
            module__isnull=True,
            code_of_type_work__in=[
                'Экзамен',
                'Другие формы контроля',
                'Зачет с оценкой',
                'Курсовая работа'
            ]
        ).select_related('discipline').prefetch_related(
            Prefetch('discipline__gradebooks', queryset=Gradebook.objects.filter(semester_number=semester_number))
        )

        if not clock_cells.exists():
            logger.warning(f"No clock cells found for curriculum {curriculum.id}, semester {semester_number}")
            continue

        # Предварительно загружаем студентов
        students = list(group.students.all())

        for clock_cell in clock_cells:
            if not clock_cell.discipline:
                logger.warning(f"Clock cell {clock_cell.id} has no discipline")
                continue

            discipline = clock_cell.discipline
            logger.debug(f"Processing discipline: {discipline.name}, type: {grade_book_type}")

            if grade_book_type == "Первичная сдача":
                gradebook = Gradebook.objects.filter(
                    discipline=discipline,
                    group=group,
                    semester_number=semester_number,
                    type_of_grade_book=grade_book_type
                ).first()

                if gradebook and gradebook.status == "Не заполнена":
                    success = update_grade_book_contingent(gradebook, students)
                    if success:
                        updated += 1
                        logger.info(f"Updated gradebook for {discipline.name}, group {group.full_name}")
                    else:
                        errors += 1
                        logger.error(f"Failed to update gradebook for {discipline.name}, group {group.full_name}")
                elif not gradebook:
                    success = create_gradebook_with_fields(
                        discipline=discipline,
                        group=group,
                        semester=semester_number,
                        grade_type=grade_book_type,
                        clock_cell=clock_cell,
                        resist_students=students
                    )
                    if success:
                        generated += 1
                        logger.info(f"Generated gradebook for {discipline.name}, group {group.full_name}")
                    else:
                        errors += 1
                        logger.error(f"Failed to generate gradebook for {discipline.name}, group {group.full_name}")
                else:
                    logger.debug(f"Gradebook already exists for {discipline.name}")
                    continue

            elif grade_book_type in ["Пересдача", "Комиссия"]:
                previous_type = "Первичная сдача" if grade_book_type == "Пересдача" else "Пересдача"
                primary_gradebook = Gradebook.objects.filter(
                    discipline=discipline,
                    group=group,
                    semester_number=semester_number,
                    type_of_grade_book=previous_type,
                    status="Закрыта"
                ).prefetch_related(
                    Prefetch(
                        'gradebookstudents_set',
                        queryset=GradebookStudents.objects.filter(grade__in=['2', 'Неявка']).select_related('student')
                    )
                ).first()

                if not primary_gradebook:
                    logger.debug(f"No {previous_type} gradebook found for {discipline.name}")
                    continue

                students_for_resit = [gs.student for gs in primary_gradebook.gradebookstudents_set.all()]

                if not students_for_resit:
                    logger.debug(f"No students for {grade_book_type} in {discipline.name}")
                    continue

                resit_gradebook = Gradebook.objects.filter(
                    discipline=discipline,
                    group=group,
                    semester_number=semester_number,
                    type_of_grade_book=grade_book_type
                ).first()

                if resit_gradebook and resit_gradebook.status == 'Не заполнена':
                    success = update_grade_book_contingent(resit_gradebook, students_for_resit)
                    if success:
                        updated += 1
                        logger.info(f"Updated {grade_book_type} gradebook for {discipline.name}, group {group.full_name}")
                    else:
                        errors += 1
                        logger.error(f"Failed to update {grade_book_type} gradebook for {discipline.name}, group {group.full_name}")
                elif not resit_gradebook:
                    success = create_gradebook_with_fields(
                        discipline=discipline,
                        group=group,
                        semester=semester_number,
                        grade_type=grade_book_type,
                        clock_cell=clock_cell,
                        resist_students=students_for_resit
                    )
                    if success:
                        generated += 1
                        logger.info(f"Generated {grade_book_type} gradebook for {discipline.name}, group {group.full_name}")
                    else:
                        errors += 1
                        logger.error(f"Failed to generate {grade_book_type} gradebook for {discipline.name}, group {group.full_name}")
                else:
                    logger.debug(f"Gradebook {grade_book_type} already exists for {discipline.name}")
                    continue

    return {
        'generated': generated,
        'updated': updated,
        'errors': errors,
        'grade_book_type': grade_book_type
    }


# Функция для получения данных таблицы
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

    group_edu_base = 9 if group.education_base == "Основное общее" else 11

    # 2. Проверяем наличие учебного плана
    curriculum = Curriculum.objects.filter(
        qualification_name=group.qualification.name,
        admission_year=group.year_create,
        basis_of_admission=group_edu_base
    )

    if not curriculum.exists():
        return None  # Учебный план не найден

    curriculum = curriculum.first()

    # Получаем дисциплины из учебного плана
    curriculum_items = ClockCell.objects.filter(
        curriculum=curriculum,
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

    grade_matrix = {}
    for student in students:
        grade_matrix[student.id] = {
            discipline.id: "-" for discipline in disciplines
        }

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

    for gb in gradebooks:
        discipline_id = gb.discipline.id
        for grade_entry in gb.grades_list:
            student = grade_entry.student
            student_id = student.id
            if student in students and grade_matrix[student_id][discipline_id] == "-":
                grade_matrix[student_id][discipline_id] = grade_entry

    quality_percentages = {}
    success_percentages = {}
    average_grades = {}
    for discipline in disciplines:
        grades = [
            grade_entry.grade if hasattr(grade_entry, 'grade') and grade_entry.grade in ["2", "3", "4", "5"]
            else 0 if str(grade_entry.grade).lower() in ['неявка', 'н/я']
            else None
            for student_id in grade_matrix
            for grade_entry in [grade_matrix[student_id][discipline.id]]
            if grade_entry != "-"
        ]
        valid_grades = [g for g in grades if g is not None]
        if valid_grades:
            total_grades = len(valid_grades)
            count_5 = sum(1 for g in valid_grades if g == "5")
            count_4 = sum(1 for g in valid_grades if g == "4")
            count_3 = sum(1 for g in valid_grades if g == "3")
            count_2 = sum(1 for g in valid_grades if g == "2")

            quality_percentages[discipline.id] = ((count_5 + count_4) / total_grades) * 100
            success_percentages[discipline.id] = ((count_5 + count_4 + count_3) / total_grades) * 100
            average_grades[discipline.id] = (
                (count_5 * 5 + count_4 * 4 + count_3 * 3 + count_2 * 2) / total_grades
            )
        else:
            quality_percentages[discipline.id] = 0.0
            success_percentages[discipline.id] = 0.0
            average_grades[discipline.id] = 0.0

    num_disciplines = len(disciplines)
    if num_disciplines > 0:
        total_quality_percentage = sum(quality_percentages.values()) / num_disciplines
        total_success_percentage = sum(success_percentages.values()) / num_disciplines
        total_average_grade = sum(average_grades.values()) / num_disciplines
    else:
        total_quality_percentage = 0.0
        total_success_percentage = 0.0
        total_average_grade = 0.0

    return {
        'students': students,
        'disciplines': disciplines,
        'grades': grade_matrix,
        'semestr': semester,
        'group': group,
        'gradebooks': gradebooks,
        'curriculum_items': curriculum_items,
        'quality_percentages': quality_percentages,
        'success_percentages': success_percentages,
        'average_grades': average_grades,
        'total_quality_percentage': total_quality_percentage,
        'total_success_percentage': total_success_percentage,
        'total_average_grade': total_average_grade,
    }