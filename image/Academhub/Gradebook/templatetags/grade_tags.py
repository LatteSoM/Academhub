import logging

from django import template

from Academhub.models import GradebookStudents

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def get_grade(student, discipline):
    """
    Возвращает самую последнюю оценку студента по дисциплине на основе даты закрытия ведомости.
    Учитывает только закрытые ведомости (status='Закрыта' и date_of_closing в прошлом).
    """
    latest_grade = student.gradebookstudents_set.filter(
        gradebook__discipline=discipline,
        gradebook__status='Закрыта'
    ).select_related('gradebook').order_by('-gradebook__date_of_closing').first()

    if latest_grade:
        logger.debug(
            f"Grade for student {student.full_name}, discipline {discipline.name}: "
            f"{latest_grade.grade} (type: {latest_grade.gradebook.type_of_grade_book}, "
            f"closed: {latest_grade.gradebook.date_of_closing})"
        )
        return latest_grade
    logger.debug(f"Grade for student {student.full_name}, discipline {discipline.name}: None")
    return None

@register.filter
def get_grade_for_semester(grade, semester):
    if grade and grade.gradebook.semester_number == semester:
        return grade
    return None

@register.filter
def filter_bad_grades(grades):
    """
    Проверяет, есть ли среди оценок плохие (2 или 'Неявка').
    Обрабатывает случаи, когда grade может быть None.
    """
    return any(grade and grade.grade in ['2', 'Неявка'] for grade in grades)

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.simple_tag
def get_semesters_order(disciplines):
    return sorted({d[1] for d in disciplines})

@register.filter
def get_all_grades(student, disciplines_with_semesters):
    """
    Возвращает все оценки студента для списка (дисциплина, семестр, часы, имя).
    """
    grades = []
    for discipline, semester, hours, display_name in disciplines_with_semesters:
        grade = GradebookStudents.objects.filter(
            student=student,
            gradebook__discipline=discipline,
            gradebook__semester_number=semester
        ).order_by('-gradebook__date_of_closing').first()
        grades.append(grade)
        logger.debug(f"Grade for {student.full_name}, {discipline.name}, semester {semester}: {grade.grade if grade else None}")
    return grades

@register.filter
def filter_valid_grades(grades):
    """
    Подсчитывает количество четвёрок и общее количество валидных оценок.
    Обрабатывает случаи, когда grade может быть None.
    """
    class GradeStats:
        def __init__(self):
            self.count_4 = 0
            self.total = 0
    stats = GradeStats()
    for grade in grades:
        if grade and grade.grade in ['2', '3', '4', '5', 'Неявка']:
            stats.total += 1
            if grade.grade == '4':
                stats.count_4 += 1
    return stats

@register.filter
def get_grade_for_discipline(student, discipline_semester):
    discipline, semester = discipline_semester
    grade_objs = student.gradebookstudents_set.filter(
        gradebook__discipline=discipline
    ).order_by('-gradebook__date_of_closing')
    return grade_objs.first()

@register.filter
def calculate_diploma_type(all_grades):
    """
    Определяет тип диплома на основе оценок.
    """
    bad_grades = [g for g in all_grades if g and str(g.grade).lower() in ['2', 'неявка', 'н/я', 'неудовлетворительно']]
    valid_grades = [g for g in all_grades if g and str(g.grade).lower() not in ['2', 'неявка', 'н/я', 'неудовлетворительно']]
    count_4 = len([g for g in valid_grades if g.grade == '4'])
    total_grades = len(valid_grades)
    return "Синий" if bad_grades or (total_grades and count_4 > total_grades * 0.25) else "Красный"

@register.filter
def filter_significant_grades(grades):
    """
    Подсчитывает количество значимых оценок (не "-").
    Обрабатывает случаи, когда grade может быть None.
    """
    class SignificantStats:
        def __init__(self):
            self.count = 0
    stats = SignificantStats()
    for grade in grades:
        if grade and grade.grade != "-":
            stats.count += 1
    return stats