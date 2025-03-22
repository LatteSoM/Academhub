import re

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
        suffix = 'Б' if student.education == 'Бюджет' else 'В'
        number = student.ancete_number if student.ancete_number else ''
        year_short = str(admission_year)[-2:]
        record_book_number = f"{prefix}{number}{suffix}/{year_short}/СПО"
        if not StudentRecordBook.objects.filter(record_book_number=record_book_number).exists():
            return record_book_number


def extract_application_number(text):
    """
    Функция для извлечения номера анкеты из колонки "Анкета абитуриента"
    """
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