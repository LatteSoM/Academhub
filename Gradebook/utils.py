import logging
import re
from datetime import datetime

from django.core.cache import cache
from django.db import transaction

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
    return code.startswith('ПМ.') and len(code.split('.')) >= 2


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


def has_required_grades(student, pm_discipline, preloaded_data):
    """
    Оптимизированная проверка наличия допустимых оценок у студента
    с использованием предзагруженных данных
    """
    pm_number = extract_pm_number(pm_discipline.code)
    if not pm_number:
        logger.warning(f"Invalid PM code: {pm_discipline.code}")
        return False

    prefixes = get_required_prefixes(pm_number)
    discipline_ids = [
        d.id for d in preloaded_data['disciplines']
        if any(str(d.code).startswith(p) for p in prefixes)
    ]

    for discipline_id in discipline_ids:
        gradebooks = preloaded_data['gradebooks_by_discipline'].get(discipline_id, [])
        if not gradebooks:
            logger.debug(f"No gradebook for discipline ID: {discipline_id}")
            return False

        latest_gradebook = gradebooks[0]
        grades = preloaded_data['grades_by_gradebook'].get(latest_gradebook.id, [])

        if not any(g.student_id == student.id and g.grade in {'3', '4', '5'} for g in grades):
            logger.debug(f"No valid grade for student {student.id} in discipline {discipline_id}")
            return False

    return True


def update_grade_book_contingent(gradebook, students, preloaded_data):
    try:
        # Оптимизированное получение преподавателей из предзагруженных данных
        teacher_link = next(
            (tl for tl in preloaded_data['teacher_links']
             if tl.discipline_id == gradebook.discipline_id and
             tl.group_id == gradebook.group_id),
            None
        )

        if teacher_link:
            gradebook.teachers.set(teacher_link.teachers.all())

        # Массовое удаление и создание записей
        with transaction.atomic():
            GradebookStudents.objects.filter(gradebook=gradebook).delete()

            GradebookStudents.objects.bulk_create([
                GradebookStudents(
                    student=student,
                    gradebook=gradebook,
                    grade='-'
                ) for student in students
            ])

        gradebook.status = 'Не заполнена'
        gradebook.save()
        return True
    except Exception as e:
        logger.error(f"Ошибка обновления ведомости: {str(e)}", exc_info=True)
        return False


def get_gradebook_name(clock_cell):
    gradebook_names = {
        "Экзамен": "Экзаменационная ведомость",
        "Зачет с оценкой": "Ведомость дифференцированного зачета",
        "Другие формы контроля": "Ведомость успеваемости",
        "Курсовая работа": "Ведомость защиты курсового проекта"
    }
    return gradebook_names.get(clock_cell.code_of_type_work, "Ведомость")


def create_gradebook_with_fields(discipline, group, semester, grade_type, clock_cell, resist_students, preloaded_data):
    try:
        # Получаем преподавателей из предзагруженных данных
        teacher_link = next(
            (tl for tl in preloaded_data['teacher_links']
             if tl.discipline_id == discipline.id and
             tl.group_id == group.id),
            None
        )

        gradebook = Gradebook.objects.create(
            discipline=discipline,
            group=group,
            semester_number=semester,
            type_of_grade_book=grade_type,
            name=get_gradebook_name(clock_cell),
            status='Не заполнена'
        )

        if teacher_link:
            gradebook.teachers.set(teacher_link.teachers.all())

        students = resist_students if resist_students else preloaded_data['students_by_group'].get(group.id, [])

        if is_pm_discipline(discipline):
            pm_number = extract_pm_number(discipline.code)
            valid_students = [
                s for s in students
                if has_required_grades(s, discipline, preloaded_data)
            ]
            students = valid_students

        # Массовое создание записей
        GradebookStudents.objects.bulk_create([
            GradebookStudents(student=student, gradebook=gradebook, grade='-')
            for student in students
        ])

        return True
    except Exception as e:
        logger.error(f"Ошибка создания ведомости: {str(e)}", exc_info=True)
        return False


def perform_generation(semester_number, grade_book_type):
    """
    Оптимизированная генерация ведомостей с предварительной загрузкой всех данных
    """
    from django.utils import timezone
    from datetime import datetime

    generated = 0
    updated = 0
    errors = 0
    current_course = (int(semester_number) + 1) // 2

    # 1. Загрузка всех необходимых данных
    logger.info("Начало загрузки данных...")

    # Все активные группы
    groups = list(GroupStudents.objects.filter(
        is_active=True,
        current_course=current_course
    ).select_related('qualification'))

    if not groups:
        logger.warning("Нет активных групп для обработки")
        return {'generated': 0, 'updated': 0, 'errors': 0, 'grade_book_type': grade_book_type}

    group_ids = [g.id for g in groups]

    # Получаем учебные планы для групп
    curriculum_ids = []
    group_curriculum_map = {}
    for group in groups:
        curriculum = group.curriculum
        if curriculum:
            curriculum_ids.append(curriculum.id)
            group_curriculum_map[group.id] = curriculum.id

    # Все студенты для этих групп
    all_students = list(Student.objects.filter(
        group_id__in=group_ids,
        is_expelled=False,
        is_in_academ=False
    ).only('id', 'group_id', 'full_name'))

    # Все учебные планы
    all_curriculums = {c.id: c for c in Curriculum.objects.filter(id__in=curriculum_ids)}

    # Все ячейки часов
    all_clock_cells = list(ClockCell.objects.filter(
        curriculum_id__in=curriculum_ids,
        term=semester_number,
        module__isnull=True,
        code_of_type_work__in=[
            'Экзамен',
            'Другие формы контроля',
            'Зачет с оценкой',
            'Курсовая работа'
        ]
    ).select_related('discipline'))

    # Все ведомости
    all_gradebooks = list(Gradebook.objects.filter(
        group_id__in=group_ids,
        semester_number=semester_number
    ).select_related('discipline', 'group'))

    # Все связи преподавателей
    all_teacher_links = list(TeachersForDisciplineAndCurriculum.objects.filter(
        group_id__in=group_ids
    ).prefetch_related('teachers'))

    # Все дисциплины для PM проверки
    pm_disciplines = list(Discipline.objects.annotate(
        clean_code=Strip('code')
    ).filter(
        Q(clean_code__startswith='МДК.') |
        Q(clean_code__startswith='УП.') |
        Q(clean_code__startswith='ПП.')
    ))

    # Все оценки для PM проверки
    gradebook_ids = [gb.id for gb in all_gradebooks]
    all_grades = list(GradebookStudents.objects.filter(
        gradebook_id__in=gradebook_ids
    ).only('id', 'gradebook_id', 'student_id', 'grade'))

    logger.info("Загрузка данных завершена")

    # 2. Подготовка структур для быстрого доступа
    students_by_group = defaultdict(list)
    for student in all_students:
        students_by_group[student.group_id].append(student)

    clock_cells_by_curriculum = defaultdict(list)
    for cc in all_clock_cells:
        clock_cells_by_curriculum[cc.curriculum_id].append(cc)

    gradebooks_by_discipline_group = defaultdict(list)
    for gb in all_gradebooks:
        key = (gb.discipline_id, gb.group_id)
        gradebooks_by_discipline_group[key].append(gb)

    teacher_links_by_group_discipline = defaultdict(list)
    for tl in all_teacher_links:
        key = (tl.group_id, tl.discipline_id)
        teacher_links_by_group_discipline[key].append(tl)

    grades_by_gradebook = defaultdict(list)
    for grade in all_grades:
        grades_by_gradebook[grade.gradebook_id].append(grade)

    # 3. Собираем все предзагруженные данные в одну структуру
    preloaded_data = {
        'students_by_group': students_by_group,
        'disciplines': pm_disciplines,
        'gradebooks_by_discipline': defaultdict(list),
        'grades_by_gradebook': grades_by_gradebook,
        'teacher_links': all_teacher_links
    }

    # Заполняем gradebooks_by_discipline
    for gb in all_gradebooks:
        preloaded_data['gradebooks_by_discipline'][gb.discipline_id].append(gb)

    # Сортируем ведомости по дате закрытия (новые сначала) с учетом timezone
    for disc_id in preloaded_data['gradebooks_by_discipline']:
        try:
            preloaded_data['gradebooks_by_discipline'][disc_id].sort(
                key=lambda x: (x.date_of_closing.astimezone(timezone.utc) if x.date_of_closing
                               else timezone.make_aware(datetime.min, timezone.utc)),
                reverse=True
            )
        except Exception as e:
            logger.error(f"Ошибка сортировки ведомостей для дисциплины {disc_id}: {str(e)}")
            # Резервный вариант сортировки без timezone
            preloaded_data['gradebooks_by_discipline'][disc_id].sort(
                key=lambda x: (x.date_of_closing.replace(tzinfo=None) if x.date_of_closing
                               else datetime.min),
                reverse=True
            )

    # 4. Обработка групп и создание ведомостей
    logger.info("Начало обработки групп...")

    for group in groups:
        curriculum_id = group_curriculum_map.get(group.id)
        if not curriculum_id:
            continue

        curriculum = all_curriculums.get(curriculum_id)
        if not curriculum:
            continue

        students = students_by_group.get(group.id, [])
        clock_cells = clock_cells_by_curriculum.get(curriculum_id, [])

        for clock_cell in clock_cells:
            if not clock_cell.discipline:
                continue

            discipline = clock_cell.discipline
            key = (discipline.id, group.id)
            gradebooks = gradebooks_by_discipline_group.get(key, [])

            if grade_book_type == "Первичная сдача":
                existing_gradebook = next(
                    (gb for gb in gradebooks if gb.type_of_grade_book == grade_book_type),
                    None
                )

                if existing_gradebook and existing_gradebook.status == "Не заполнена":
                    if update_grade_book_contingent(existing_gradebook, students, preloaded_data):
                        updated += 1
                    else:
                        errors += 1
                elif not existing_gradebook:
                    if create_gradebook_with_fields(
                            discipline=discipline,
                            group=group,
                            semester=semester_number,
                            grade_type=grade_book_type,
                            clock_cell=clock_cell,
                            resist_students=students,
                            preloaded_data=preloaded_data
                    ):
                        generated += 1
                    else:
                        errors += 1

            elif grade_book_type in ["Пересдача", "Комиссия"]:
                previous_type = "Первичная сдача" if grade_book_type == "Пересдача" else "Пересдача"
                primary_gradebook = next(
                    (gb for gb in gradebooks
                     if gb.type_of_grade_book == previous_type and
                     gb.status == "Закрыта"),
                    None
                )

                if not primary_gradebook:
                    continue

                # Получаем студентов с неудовлетворительными оценками
                failed_grades = grades_by_gradebook.get(primary_gradebook.id, [])
                failed_student_ids = {
                    g.student_id for g in failed_grades
                    if g.grade in ['2', 'Неявка']
                }

                students_for_resit = [
                    s for s in students
                    if s.id in failed_student_ids
                ]

                if not students_for_resit:
                    continue

                resit_gradebook = next(
                    (gb for gb in gradebooks if gb.type_of_grade_book == grade_book_type),
                    None
                )

                if resit_gradebook and resit_gradebook.status == 'Не заполнена':
                    if update_grade_book_contingent(resit_gradebook, students_for_resit, preloaded_data):
                        updated += 1
                    else:
                        errors += 1
                elif not resit_gradebook:
                    if create_gradebook_with_fields(
                            discipline=discipline,
                            group=group,
                            semester=semester_number,
                            grade_type=grade_book_type,
                            clock_cell=clock_cell,
                            resist_students=students_for_resit,
                            preloaded_data=preloaded_data
                    ):
                        generated += 1
                    else:
                        errors += 1

    logger.info(f"Обработка завершена. Сгенерировано: {generated}, Обновлено: {updated}, Ошибок: {errors}")
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