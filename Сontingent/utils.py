import re
from Academhub.models import *
from django.db import transaction
from django.utils import timezone
from django.core.files.base import equals_lf


def generate_unique_record_book_number(admission_year, student):
    """
    Функция для генерации уникального номера зачетной книжки
    prefix: 'Д' - ('Д' означает "Дневная форма обучения", этот префикс в номере зачетной книжки не меняется)
    suffix - 'Б' или'В' - ('Б' если у студента основа обучения "Бюджет", 'В' если основа обучения "Внебюджет")
    number - цифры в номере зачетной книжки подтягивается из анкеты на поступление
    year_short - короткое отображение года поступления (пример: 2025 станет 25)
    record_book_number - итоговый номер зачетной книжки  если функция отработала правильно, бедт иметь вид: "Д1593Б/21/СПО"
    """
    while True:
        prefix = 'Д'
        suffix = 'Б' if student.education_basis == 'бюджет' else 'В'
        number = student.ancete_number if student.ancete_number else ''
        year_short = str(admission_year)[-2:]
        record_book_number = f"{prefix}{number}{suffix}/{year_short}/СПО"
        if not StudentRecordBook.objects.filter(record_book_number=record_book_number).exists():
            return record_book_number

def get_term_papers_for_recordbook(clock_cells):
    """
        Фильтруем только часы курсовых работ
    """
    term_papers = []

    for clock_cell in clock_cells:
        try:
            ClockCell.objects.get(
                disciplin=clock_cell.discipline,
                code_of_type_work = "Курсовая работа"
            )

            term_papers.append(clock_cell)
        except:
            pass
    
    return term_papers

def get_professional_modules_for_recordbook(clock_cells):
    """
        Фильтруем только часы профессиональных модулей
    """
    return clock_cells.filter(
        module_id__isnull=False, 
        discipline__isnull=True, 
    )

def get_disciplines_and_practices_for_recordbook(clock_cells, term_papers):
    """
        Фильтруем дисциплины и практики
    """
    clock_cells_disciplines = []
    clock_cells_practices = []

    clock_cells_disciplines_and_practices = clock_cells.filter(
        module_id__isnull=False, 
        discipline__isnull=True, 
    )

    for clock_cell in clock_cells_disciplines_and_practices:
        if clock_cell in term_papers:
            continue
        
        if clock_cell.discipline.code in "УП" or clock_cell.discipline.code in "ПП":
            clock_cells_practices.append(clock_cell)
        else:
            clock_cells_disciplines.append(clock_cell)

    return clock_cells_disciplines, clock_cells_practices

def create_recordbook_template(qualification: Qualification):
    curiculum = qualification.study_plan

    #1) список дисциплин
    #2) + форма аттестации
    #3) + количество часов
    
    # Все часы учебного плана
    clock_cells = ClockCell.objects.filter(curiculum=curiculum, code_of_type_work='Итого часов')



def extract_application_number(text):
    """
    Функция для извлечения номера анкеты из колонки "Анкета абитуриента"
    """
    if not isinstance(text, str):  # Проверяем, что text является строкой
        return None
    match = re.search(r"Заявление о поступлении (\d+)-?(\d*) от", text)
    if match:
        if match.group(2):  # Если есть вторая часть (пример: "427-696")
            return match.group(1) + "-" + match.group(2)
        return match.group(1).lstrip("0")  # Убираем нули, если одинарный номер

    return None  # Если не найдено возвращается Ноне

def student_format_to_list():
    students = []
    for student in Student.objects.all():
        student_specialty = student.group.qualification.specialty
        student_qualification = student.group.qualification.name
        student_current_course = student.group.current_course
        student_education_base = student.education_base
        student_education_basis = student.education_basis
        student_is_in_academ = student.is_in_academ
        student_is_expelled = student.is_expelled

        students.append({"specialty_code": student_specialty.code, "specialty_name": student_specialty.name,
                         "qualification": student_qualification,
                         "course": student_current_course, "base": student_education_base, "budget": student_education_basis,
                         "academic_leave": student_is_in_academ, "is_expelled": student_is_expelled})
    return students


def transfer_group(group_id):
    """
    Перевод группы на следующий курс
    Если группа на 4 курсе - деактивируем ее
    """
    group = GroupStudents.objects.get(id=group_id)

    if group.current_course < 4:
        group.current_course += 1
        group.save()
    elif group.current_course == 4:
        group.is_active = False
        group.save()

def transfer_group_students(group_id, transfer_order):
    """
    Перевод всех студентов группы на следующий курс с указанием приказа
    Если группа на 4 курсе - деактивирует группу и не переводит студентов, ну и логично деактивирует студентов
    """
    transfer_group(group_id)
    group = GroupStudents.objects.get(id=group_id)
    students = Student.objects.filter(group=group, is_expelled=False, is_in_academ=False)

    if group.current_course < 4:
        order_field_map = {
            2: 'transfer_to_2nd_year_order',
            3: 'transfer_to_3rd_year_order',
            4: 'transfer_to_4th_year_order'
        }

        new_course = group.current_course
        order_field = order_field_map.get(new_course)
        for student in students:
            setattr(student, order_field, transfer_order)
            student.save()

        return True, f"Группа {group.full_name} и все студенты успешно переведены на курс"

    elif group.current_course == 4:
        group.is_active = False
        group.save()
        return True, f"Группа {group.full_name} деактивирована (4 курс завершен)"
#
    # except GroupStudents.DoesNotExist:
    #     return False, "Группа не найдена"
    # except Exception as e:
    #     return False, f"Ошибка при переводе: {str(e)}"


def create_transfer_log(order_number, student):
    ContingentMovement.objects.create(
        order_number=order_number,
        action_type='transfer_course',
        action_date=timezone.now().date(),
        previous_group=student.group,
        new_group=None,
        student=student,
    )
