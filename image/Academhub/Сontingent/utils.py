import re

from django.utils import timezone

from Academhub.models import *


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
        # if not StudentRecordBook.objects.filter(record_book_number=record_book_number).exists():
        return record_book_number


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


def get_middle_certifications(clock_cells):
    middle_certifications = {
        'exam': [],
        'credit': [],
    }

    attestation_form = ['Экзамен', 'Зачет с оценкой', 'Другие формы контроля']

    discipline = None
    semestr = None
    hours = None
    is_exam = False

    for clock_cell in clock_cells:

        if clock_cell.module is None and clock_cell.code_of_type_work in attestation_form \
                and not clock_cell.discipline.name.__contains__('Экзамен') \
                and not clock_cell.discipline.name.__contains__('Учебная практика') \
                and not clock_cell.discipline.name.__contains__('Производственная практика'):
            if clock_cell.code_of_type_work == 'Экзамен':
                is_exam = True
            discipline = clock_cell.discipline
            semestr = clock_cell.term
            # print(discipline, semestr)

        if discipline and semestr:
            # print('2 ifffffffff')
            if clock_cell.code_of_type_work == 'Итого часов' \
                    and clock_cell.discipline == discipline and clock_cell.term == semestr:
                # print('3 ifffffffff')

                hours = clock_cell.count_of_clocks
                if is_exam:
                    # print('4 ifffffffff')

                    middle_certifications['exam'].append({
                        'name': discipline.name,
                        'hours': hours,
                        'semester': semestr
                    })
                    is_exam = False

                else:
                    # print('4 ifffffffff elsseeee')

                    middle_certifications['credit'].append({
                        'name': discipline.name,
                        'hours': hours,
                        'semester': semestr
                    })
                discipline = None
                semestr = None
                hours = None

    # print(middle_certifications)
    return middle_certifications

def get_practices(clock_cells):
    practices = {
        'study_practice': [],
        'work_practice': [],
    }

    practices_code = ['УП', 'ПП']

    discipline = None
    semestr = None
    hours = None

    for clock_cell in clock_cells:
        if clock_cell.module is None:
            clock_cell_discipline = Discipline.objects.get(pk=clock_cell.discipline_id)
            if practices_code[0] in clock_cell_discipline.code \
                or practices_code[1] in clock_cell_discipline.code :
                discipline = f'{str(clock_cell_discipline.code).strip()} {clock_cell_discipline.name}'
                semestr = clock_cell.term

        if discipline and semestr:
            if clock_cell.code_of_type_work == 'Итого часов':
                hours = clock_cell.count_of_clocks

                if practices_code[0] in clock_cell.discipline.code:
                    practices['study_practice'].append([
                        discipline,
                        semestr,
                        hours
                    ])
                else:
                    practices['work_practice'].append([
                        discipline,
                        semestr,
                        hours
                    ])
        discipline = None
        semestr = None
        hours = None
    return practices


def get_professional_modules(clock_cells):
    professional_modules = {
        'professional_modules': [],
    }

    for clock_cell in clock_cells:
        if clock_cell.module is not None:
            module = Module.objects.get(pk=clock_cell.module_id)
            if str(module.code_of_discipline).strip().__contains__('ПМ') and \
                    [f'{module.code_of_discipline.strip()} {module.name}'] not in professional_modules['professional_modules']:
                professional_modules['professional_modules'].append([
                    f'{module.code_of_discipline.strip()} {module.name}',
                ])
    return professional_modules


def get_term_papers(clock_cells):
    term_papers = {
        'term_papers': [],
    }
    for clock_cell in clock_cells:
        if clock_cell.module is None and clock_cell.code_of_type_work == 'Курсовая работа':
            clock_cell_discipline = Discipline.objects.get(pk=clock_cell.discipline_id)
            if [clock_cell_discipline.name] not in term_papers['term_papers']:
                term_papers['term_papers'].append([
                    clock_cell_discipline.name,
                ])


    return term_papers


def create_template_recordbook_view(recordbook: StudentRecordBook):
    curiculum = Curriculum.objects.get(pk=recordbook.curriculum.pk)
    # print(curiculum)
    clock_cells = ClockCell.objects.filter(curriculum=curiculum.pk)
    # print(clock_cells)

    middle_certifications = get_middle_certifications(clock_cells)
    print(middle_certifications)
    semesters = set()
    for exam in middle_certifications['exam']:
        semesters.add(exam['semester'])
    for credit in middle_certifications['credit']:
        semesters.add(credit['semester'])

    practices = get_practices(clock_cells)
    # print(practices)
    professional_modules = get_professional_modules(clock_cells)
    # print(professional_modules)
    term_papers = get_term_papers(clock_cells)
    # print(term_papers)
    template = {
        'middle_certifications': middle_certifications,
        'practices': practices,
        'professional_modules': professional_modules,
        'term_papers': term_papers,
        'semesters': sorted(semesters)
    }
    # print(template)
    return template
